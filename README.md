# GitLoom

GitLoom is a command-line tool that generates text continuations using the Anthropic API (Claude models) and manages different versions of the text using Git. It automatically creates branches for new continuations, allowing you to explore multiple paths of text generation. You can rewind to earlier versions of the text using standard Git commands.

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


## **What GitLoom Does**

1. **Text Continuation**:
   - GitLoom uses the Anthropic API to generate continuations of a text file.
   - It appends the continuation to the file and commits the changes to a Git repository.

2. **Git Integration**:
   - GitLoom initializes a Git repository if one doesn’t already exist.
   - It automatically creates new branches for continuations when you’re in a detached HEAD state (e.g., after rewinding to an earlier commit).
   - Each branch is named based on the first 10 characters of the continuation and a timestamp (e.g., `branch_HelloWor_20231025_1530`).

3. **Dry Run Mode**:
   - You can use the `--dry-run` option to generate a continuation without modifying the file or committing changes.

---

## **How to Run GitLoom**

### **Basic Usage**
1. Run the command:
   ```bash
   gitloom
   ```
   - By default, it reads from and writes to a file named `untitled.txt`.

2. Specify a different file:
   ```bash
   gitloom --file myfile.txt
   ```

3. Provide initial text:
   ```bash
   gitloom "This is the starting text."
   ```

4. Use dry-run mode (no changes to the file or repository):
   ```bash
   gitloom --dry-run
   ```

---

## **How to Rewind the Text**

GitLoom uses Git to manage different versions of the text. You can use standard Git commands to rewind to earlier versions.

### **1. View Commit History**
To see the commit history, including branch names and commit messages:
```bash
git log --oneline --graph --all
```

### **2. Checkout an Earlier Commit**
To rewind to an earlier commit, use `git checkout` with the commit hash:
```bash
git checkout abc1234
```

### **3. Checkout the nth Previous Commit**
To rewind to the nth previous commit, use `HEAD~n`:
```bash
git checkout HEAD~3
```
This will rewind to the 3rd previous commit.

### **4. Checkout a Branch**
To switch to a specific branch:
```bash
git checkout branch_HelloWor_20231025_1530
```

### **5. Return to the Latest Commit**
To return to the latest commit on the main branch:
```bash
git checkout main
```

### **6. Create a New Branch**
If you want to explore a new continuation from an earlier commit, create a new branch:
```bash
git checkout -b new-branch-name
```

---

## **Example Workflow**

1. Generate a continuation:
   ```bash
   gitloom
   ```

2. View the commit history:
   ```bash
   git log --oneline --graph --all
   ```

3. Rewind to the 2nd previous commit:
   ```bash
   git checkout HEAD~2
   ```

4. Generate a new continuation from the rewound state:
   ```bash
   gitloom
   ```

---

## **Command-Line Options**

| Option            | Description                                      |
|-------------------|--------------------------------------------------|
| `--file`, `-f`    | File to read from/write to (default: `untitled.txt`). |
| `--model`, `-m`   | Model to use for text generation (default: `claude-3-5-sonnet-20241022`). |
| `--temperature`, `-t` | Temperature for text generation (default: `1.0`). |
| `--max-tokens`, `-mt` | Maximum number of tokens to generate (default: `1024`). |
| `--system`, `-s`  | System prompt for the model (default: CLI simulation mode). |
| `--user-message`, `-u` | Content of the user message (default: `<cmd>cat untitled.txt</cmd>`). |
| `--dry-run`, `-d` | Do not edit the file or commit changes, just print the continuation. |

---

## **License**
GitLoom is open-source and available under the MIT License.
