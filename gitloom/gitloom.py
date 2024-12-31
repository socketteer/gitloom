import anthropic
import os
import argparse
import re
from git import Repo  # GitPython library
from datetime import datetime

client = anthropic.Anthropic()  # Will use ANTHROPIC_API_KEY from environment

DEFAULT_STORAGE_FILE = "untitled.txt"
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 1024
DEFAULT_SYSTEM = "The assistant is in CLI simulation mode, and responds to the user's CLI commands only with the output of the command."
DEFAULT_USER_MESSAGE = "<cmd>cat untitled.txt</cmd>"

def sanitize_branch_name(name):
    """
    Sanitize a string to make it a valid Git branch name.
    - Replace illegal characters with underscores.
    - Truncate to a reasonable length.
    - Ensure the name isn't empty.
    """
    # Replace illegal characters with underscores
    sanitized = re.sub(r"[~^: *?\[\]@\\/]", "_", name)
    
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


def get_continuation(text, model, temperature, max_tokens, system, user_message):
    try:
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": text}
        ]
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages
        )
        if not response.content:
            print("Error: No content in response")
            return ""
        return response.content[0].text
    except Exception as e:
        print(f"[Error: {str(e)}]")
        return ""

def initialize_repo(file_path):
    """Initialize a Git repository if it doesn't already exist."""
    repo_dir = os.path.dirname(os.path.abspath(file_path)) or "."
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        print(f"Initializing Git repository in {repo_dir}")
        Repo.init(repo_dir)
    return Repo(repo_dir)

def commit_changes(repo, file_path, commit_message=None):
    """Stage and commit changes to the file, handling detached HEAD state."""

    # Check if in detached HEAD state
    if repo.head.is_detached:
        # Create a new branch name based on the continuation and timestamp
        branch_name = create_branch_name(commit_message)
        # print(f"Creating new branch: {branch_name}")
        checkout_output = repo.git.checkout("-b", branch_name)
        print(checkout_output)
    
    # Commit the changes
    # if not commit_message:
    #     commit_message = (
    #         f"+{continuation[:50]}..."  # Include the first 50 chars of the continuation
    #     )
    repo.git.add(file_path)
    commit_output = repo.git.commit("-m", commit_message)
    print(commit_output)

def main():
    parser = argparse.ArgumentParser(description='Generate text continuations using Claude')
    parser.add_argument('--file', '-f', default=DEFAULT_STORAGE_FILE,
                      help='File to read from/write to (default: untitled.txt)')
    parser.add_argument('--model', '-m', default=DEFAULT_MODEL,
                      help=f'Model to use for text generation (default: {DEFAULT_MODEL})')
    parser.add_argument('--temperature', '-t', type=float, default=DEFAULT_TEMPERATURE,
                      help=f'Temperature for text generation (default: {DEFAULT_TEMPERATURE})')
    parser.add_argument('--max-tokens', '-mt', type=int, default=DEFAULT_MAX_TOKENS,
                      help=f'Maximum number of tokens to generate (default: {DEFAULT_MAX_TOKENS})')
    parser.add_argument('--system', '-s', default=DEFAULT_SYSTEM,
                      help=f'System prompt for the model (default: {DEFAULT_SYSTEM})')
    parser.add_argument('--user-message', '-u', default=DEFAULT_USER_MESSAGE,
                      help=f'Content of the user message (default: {DEFAULT_USER_MESSAGE})')
    parser.add_argument('--dry-run', '-d', action='store_true',
                      help='Do not edit the file or commit changes, just print the continuation')
    parser.add_argument('text', nargs='*', default=[],
                      help='Initial text (if not reading from file)')
    
    args = parser.parse_args()
    storage_file = args.file
    
    if not args.dry_run:
        # Initialize Git repository
        repo = initialize_repo(storage_file)
    
    # If file doesn't exist and we have initial text, initialize it
    if not os.path.exists(storage_file) and args.text:
        initial_text = " ".join(args.text)
        with open(storage_file, "w") as f:
            f.write(initial_text)

        if not args.dry_run:
            # Commit the initial file
            commit_changes(repo, storage_file, initial_text)
    
    # Read current text
    if os.path.exists(storage_file):
        with open(storage_file, "r") as f:
            current_text = f.read()

        if not args.dry_run:
            # if there are uncommitted changes, commit them
            if repo.is_dirty():
                commit_changes(repo, storage_file, current_text, "Uncommitted changes")
        
        # Get and print continuation
        continuation = get_continuation(current_text, args.model, args.temperature, args.max_tokens, args.system, args.user_message)
        if continuation:
            # print(continuation)
            
            if not args.dry_run:
                # Save updated text
                with open(storage_file, "w") as f:
                    f.write(current_text + continuation)
                
                # Commit the changes
                commit_changes(repo, storage_file, continuation)
            else:
                print(continuation)
    else:
        print("No input file found and no initial text provided.")

if __name__ == "__main__":
    main()