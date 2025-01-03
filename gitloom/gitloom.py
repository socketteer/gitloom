import anthropic
import os
import argparse
import re
import json
import jsonlines
from git import Repo  # GitPython library
from datetime import datetime

client = anthropic.Anthropic()  # Will use ANTHROPIC_API_KEY from environment


DEFAULT_SETTINGS = {
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 1.0,
    "max_tokens": 1024,
}

DEFAULT_BASE_SETTINGS = {
    "mode": "base",
    "file": "untitled.txt",
    "system": "The assistant is in CLI simulation mode, and responds to the user's CLI commands only with the output of the command.",
    "user_message": "<cmd>cat untitled.txt</cmd>"
}

DEFAULT_CHAT_SETTINGS = {
    "mode": "chat",
    "file": "chat.jsonl",
}

DEFAULT_SETTINGS_FILE = "settings.json"

# DEFAULT_MODE = "base"

def load_settings(settings_file_path=None, mode="base"):
    settings = DEFAULT_SETTINGS
    if mode == "base":
        settings.update(DEFAULT_BASE_SETTINGS)
    elif mode == "chat":
        settings.update(DEFAULT_CHAT_SETTINGS)
    else:
        raise ValueError(f"Invalid mode: {mode}")
    
    if settings_file_path:
        file_path = settings_file_path
    else:
        file_path = DEFAULT_SETTINGS_FILE
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                file_settings = json.load(f)
                settings.update(file_settings)
            print(f"Loaded settings from {file_path}")
    except Exception as e:
        print(f"Warning: Could not load settings file: {e}")
    
    return settings



def sanitize_branch_name(name):
    """
    Sanitize a string to make it a valid Git branch name.
    - Replace illegal characters with underscores.
    - Replace whitespace (including newlines) with underscores.
    - Truncate to a reasonable length.
    - Ensure the name isn't empty.
    """
    # Replace whitespace and illegal characters with underscores
    sanitized = re.sub(r"[\s~^: *?\[\]@\\/]", "_", name)
    
    # Truncate to 50 characters (Git allows up to 255, but shorter is better)
    sanitized = sanitized[:50]
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip("_.")
    
    # If the name is empty after sanitization, use a fallback
    if not sanitized:
        sanitized = "branch"
    
    return sanitized

def create_branch_name(continuation):
    """
    Create a unique branch name based on the continuation and a timestamp.
    """
    # Sanitize the continuation prefix
    prefix = sanitize_branch_name(continuation[:10])  # Use first 10 chars
    
    # Add a timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine prefix and timestamp
    return f"{prefix}_{timestamp}"


def get_continuation(input, settings):
    
    try:
        if settings["mode"] == "base":
            messages = [
                {"role": "user", "content": settings["user_message"]},
                {"role": "assistant", "content": input}
            ]
        else:
            messages = input

        params = {}

        for key in ["model", "max_tokens", "temperature", "system"]:
            if key in settings and settings[key]:
                params[key] = settings[key]

        # print('params', params)
            
        response = client.messages.create(
            messages=messages,
            **params
        )
        if not response.content:
            print("Error: No content in response")
            return ""
        return response.content[0].text
    except Exception as e:
        print(f"API Error: {str(e)}")
        return ""
    

def initialize_repo(file_path):
    """Initialize a Git repository if it doesn't already exist."""
    repo_dir = os.path.dirname(os.path.abspath(file_path)) or "."
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        print(f"Initializing Git repository in {repo_dir}")
        repo = Repo.init(repo_dir)
        # Configure to suppress detached HEAD warnings
        with repo.config_writer() as config:
            config.set_value("advice", "detachedHead", False)
    return Repo(repo_dir)


def get_diff_changes(repo, file_path):
    """Extract only the added and deleted parts from a word-diff."""
    diff = repo.git.diff("--word-diff", file_path)

    # print('diff', diff)
    
    # Find all additions (text between {+ and +})
    additions = re.findall(r'\{\+(.*?)\+\}', diff)
    
    # Find all deletions (text between [- and -])
    deletions = re.findall(r'\[-(.*?)-\]', diff)
    
    return {
        'added': additions,
        'deleted': deletions,
        'diff': diff
    }

def commit_changes(repo, file_path, commit_message=None):
    """Stage and commit changes to the file, handling detached HEAD state."""


    if not commit_message:
        # if no commit message, get the diff of the file
        changes = get_diff_changes(repo, file_path)
        commit_message = ""
        for change in changes['added']:
            commit_message += f"+{change}\n"
        for change in changes['deleted']:
            commit_message += f"-{change}\n"

        if not commit_message:
            commit_message = changes['diff']

    if not commit_message:
        commit_message = "Uncommitted changes"

    # Check if in detached HEAD state
    if repo.head.is_detached:
        # Create a new branch name based on the continuation and timestamp
        branch_name = create_branch_name(commit_message)
        # print(f"Creating new branch: {branch_name}")
        checkout_output = repo.git.checkout("-b", branch_name)
        print(checkout_output)

    # Commit the changes
    repo.git.add(file_path)

    commit_output = repo.git.commit("-m", commit_message)
    print(commit_output)


def main():
    parser = argparse.ArgumentParser(description='Generate text continuations using Claude')
    parser.add_argument('--mode', default="base",
                      help='Mode to use for text generation, "base" or "chat" (default: base)')
    parser.add_argument('--settings', default=None,
                      help='Path to settings JSON file (default: settings.json in current directory)')
    parser.add_argument('--file', '-f', default=None,
                      help='File to read from/write to (default: from settings or untitled.txt if base mode and chat.jsonl if chat mode)')
    parser.add_argument('--model', '-m', default=None,
                      help='Model to use for text generation')
    parser.add_argument('--temperature', '-t', type=float, default=None,
                      help='Temperature for text generation')
    parser.add_argument('--max-tokens', '-mt', type=int, default=None,
                      help='Maximum number of tokens to generate')
    parser.add_argument('--system', '-s', default=None,
                      help='System prompt for the model')
    parser.add_argument('--user-message', '-u', default=None,
                      help='Content of the user message (base mode only)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                      help='Do not edit the file or commit changes, just print the continuation')
    parser.add_argument('text', nargs='*', default=[],
                      help='Text in user message (chat) or to append to file prior to continuation (base)')
    
    args = parser.parse_args()

    settings = load_settings(args.settings, args.mode)
    args_dict = {k: v for k, v in vars(args).items() if v is not None}
    settings.update(args_dict)
    storage_file = settings["file"]
    
    if not args.dry_run:
        repo = initialize_repo(storage_file)

    input_text = " ".join(args.text) if args.text else ""
    if args.mode == "base":
        input = input_text
        current = ""
    elif args.mode == "chat":
        if input_text:
            input = [{"role": "user", "content": input_text}]
        else:
            input = []
        current = []


    if not args.dry_run:
        # if file does not exist, create an empty file
        if not os.path.exists(storage_file):
            with open(storage_file, "w") as f:
                f.write("")
            commit_changes(repo, storage_file, "create empty file")
        # if file exists but is not tracked, add it
        elif repo.git.status(storage_file, porcelain=True).startswith('??'):
            print(f"Debug: File status: {repo.git.status(storage_file, porcelain=True)}")  # Add this line
            commit_changes(repo, storage_file, "add existing file")
        else:
            print(f"Debug: File exists but not untracked. Status: {repo.git.status(storage_file, porcelain=True)}")  # Add this line

        if input_text:
            # append input to file
            if args.mode == "base":
                with open(storage_file, "a") as f:
                    f.write(input)
            elif args.mode == "chat":
                with jsonlines.open(storage_file, "a") as f:
                    f.write_all(input)
            commit_changes(repo, storage_file)

    # get current state of file
    if os.path.exists(storage_file):
        if args.mode == "base":
            with open(storage_file, "r") as f:
                current = f.read().strip()
        elif args.mode == "chat":
            with jsonlines.open(storage_file, "r") as f:
                current = [message for message in f]

    
    if args.dry_run:
        current = current + input
        current = current.strip()


    # Get and print continuation
    continuation = get_continuation(current, settings)
    if continuation:
        # print(continuation)
        
        if not args.dry_run:
            if args.mode == "base":
                # Save updated text
                with open(storage_file, "w") as f:
                    f.write(current + continuation)
                # Commit the changes
                # commit_changes(repo, storage_file, f'+{continuation}')
            elif args.mode == "chat":
                # Save updated text
                with jsonlines.open(storage_file, "a") as f:
                    f.write({"role": "assistant", "content": continuation})
                # Commit the changes
                # commit_changes(repo, storage_file, f'+{continuation}')
            # if there are uncommitted changes, commit them
            if repo.is_dirty():
                commit_changes(repo, storage_file)
        else:
            print(continuation)

if __name__ == "__main__":
    main()