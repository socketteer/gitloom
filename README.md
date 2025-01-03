# GitLoom

GitLoom is a command-line tool that generates text continuations using the Anthropic API (Claude models) and manages different versions of the text using Git. It supports both standard text generation and chat modes, and automatically creates branches for new continuations, allowing you to explore multiple paths of text generation.

---

## **Important Usage Notes**

- GitLoom creates a new Git repository in the directory where you run it
- Each text file and its version history should be in its own directory
- Do not run GitLoom in an existing Git repository, as this will cause conflicts
- Create a new directory for each text project you want to work on

For example:
```bash
# Good: Create separate directories for different projects
mkdir my-story
cd my-story
gitloom "Once upon a time"

# Later, for a different project:
mkdir my-chat
cd my-chat
gitloom --mode chat "Hello, Claude!"
```

---

## **Installation**

1. Install Python 3.
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/gitloom.git
   cd gitloom
   ```
3. Install the package:
   ```bash
   pip install -e .
   ```
4. Set the `ANTHROPIC_API_KEY` environment variable with your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

## **Modes**

GitLoom supports two modes of operation:

1. **Base Mode** (default):
   - Generates continuations of text files
   - Uses untitled.txt by default
   - Each continuation is appended to the existing text

2. **Chat Mode**:
   - Maintains a conversation with Claude
   - Uses chat.jsonl by default
   - Stores conversation history in JSONL format

## **Settings**

GitLoom can be configured using a settings.json file in your working directory. Example settings:

```json
{
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 1.0,
    "max_tokens": 1024,
    "system": "Custom system prompt",
    "mode": "base",
    "file": "custom.txt"
}
```

## **Command-Line Options**

| Option            | Description                                      |
|-------------------|--------------------------------------------------|
| `--mode`          | Mode to use: "base" or "chat" (default: "base") |
| `--settings`      | Path to settings JSON file |
| `--file`, `-f`    | File to read from/write to (default depends on mode) |
| `--model`, `-m`   | Model to use for text generation |
| `--temperature`, `-t` | Temperature for text generation (default: 1.0) |
| `--max-tokens`, `-mt` | Maximum number of tokens to generate (default: 1024) |
| `--system`, `-s`  | System prompt for the model |
| `--user-message`, `-u` | Content of the user message (base mode only) |
| `--dry-run`, `-d` | Do not edit the file or commit changes, just print the continuation |

## **Examples**

### Base Mode
```bash
# Start a new text file
gitloom "Once upon a time"

# Continue existing text
gitloom

# Use a custom file
gitloom --file story.txt "Chapter 1"
```

### Chat Mode
```bash
# Start a new chat
gitloom --mode chat "Hello, Claude!"

# Continue existing chat
gitloom --mode chat "Tell me more"

# Use custom settings
gitloom --mode chat --temperature 0.7 "Let's be creative"
```

## **Git Integration**

GitLoom automatically:
- Initializes a Git repository if one doesn't exist
- Creates new branches when continuing from an earlier point
- Commits changes with descriptive messages
- Names branches based on the content and timestamp

### View History and Rewind
```bash
# View commit history
git log --oneline --graph --all

# Rewind to earlier version
git checkout <commit-hash>

# Generate new continuation from that point
gitloom
```

---

## **License**
GitLoom is open-source and available under the MIT License.