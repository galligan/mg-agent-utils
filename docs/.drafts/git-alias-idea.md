# Git Config for Agent-Driven Development

## Git Config Setup

Use Cursor to edit `gitconfig` files & set up an alias for `git config` to open the global config file in Cursor:

```bash
git config --global core.editor "/Applications/Cursor.app/Contents/MacOS/Cursor" && git config --global alias.ec '!f() { git config --global --edit; }; f'
```

Use `| cat` for all commands for better compatibility with agentic development

```bash
# Disable paging but keep colors
git config --global core.pager cat

# Keep colors when piping (e.g. `git status | cat`)
git config --global color.ui always
```

Optional: If you want to use pagination for other commands, you can set up aliases for them:

```bash
git config --global alias.plog 'log --pager=less' # Paginate log output
git config --global alias.pdiff 'diff --pager=less' # Paginate diff output
git config --global alias.pshow 'show --pager=less' # Paginate show output
git config --global alias.pblame 'blame --pager=less' # Paginate blame output
```

## Git Aliases

### Git Commits

#### Git Commit Message

`git cm` is a custom alias for `git commit` that checks for conventional commits and allows for optional multi-line commit messages written in a separate file. This approach is useful for guiding the agent to write a properly formatted commit message.

Usage:

- `git cm "type(scope): description"` - Commit with message
- `git cm "type(scope): description" desc.txt` - Commit with message and multi-line description file

```ini
[alias]
  # Commit with message, check for conventional commits
  cm = "!f() { \
    RED=\"\\033[0;31m\"; \
    GREEN=\"\\033[0;32m\"; \
    YELLOW=\"\\033[0;33m\"; \
    NC=\"\\033[0m\"; \
    COMMIT_TITLE=\"$1\"; \
    DESC_FILE=\"$2\"; \
    LINE_BREAK='=============================================================='; \
    SUB_BREAK='~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'; \
    if [ -z \"$COMMIT_TITLE\" ]; then \
      echo \"${RED}❌ ERROR: No commit message provided${NC}\"; \
      echo \"$LINE_BREAK\"; \
      echo \"📝 Usage: git cm \\\"type(scope): description\\\" [description-file (optional for multi-line)]\"; \
      echo \"👉 Example: git cm \\\"feat(auth): add login button\\\" COMMIT_DESC.tmp\"; \
      return 1; \
    fi; \
    COMMIT_LENGTH=${#COMMIT_TITLE}; \
    if [ $COMMIT_LENGTH -gt 70 ]; then \
      echo \"${RED}❌ ERROR: Commit message is too long (${COMMIT_LENGTH} chars)${NC}\"; \
      echo \"$LINE_BREAK\"; \
      echo \"📏 Rule: Commit title should be 70 characters or less\"; \
      echo \"💡 Suggestion: Shorten title or include a temp file for more lines e.g. (COMMIT_DESC.tmp):\"; \
      echo \"👉 git cm \\\"type(scope): description\\\" COMMIT_DESC.tmp\"; \
      return 1; \
    fi; \
    COMMIT_REGEX='^(feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert|hotfix|release)(\\([a-z0-9-]+\\))?: .+$'; \
    if ! [[ $COMMIT_TITLE =~ $COMMIT_REGEX ]]; then \
      echo \"${RED}❌ ERROR: Commit message does not follow conventional commits${NC}\"; \
      echo \"$LINE_BREAK\"; \
      echo \"📝 Format: type(scope): description\"; \
      echo \"👉 Examples: \\\"feat(auth): add login button\\\", \\\"fix: resolve null pointer exception\\\"\"; \
      echo \"✅ Valid types: feat, fix, docs, style, refactor, test, chore, perf, build, ci, revert, hotfix, release\"; \
      return 1; \
    fi; \
    if [ -n \"$DESC_FILE\" ] && [ -f \"$DESC_FILE\" ]; then \
      printf \"%s\\n\\n\" \"$COMMIT_TITLE\" > .git/COMMIT_EDITMSG; \
      cat \"$DESC_FILE\" >> .git/COMMIT_EDITMSG; \
      git commit -F .git/COMMIT_EDITMSG; \
      COMMIT_STATUS=$?; \
      if [ $COMMIT_STATUS -eq 0 ]; then \
        COMMIT_HASH=$(git rev-parse --short HEAD); \
        echo \"${GREEN}✅ Commit successful! Created commit $COMMIT_HASH${NC}\"; \
        echo \"$LINE_BREAK\"; \
        echo \"📝 Message: $COMMIT_TITLE\"; \
        echo \"$SUB_BREAK\"; \
        echo \"🔄 Files changed:\"; \
        echo \"$(git diff --stat HEAD~1 HEAD | grep -v 'files changed' | sed 's/^  / /')\"; \
        echo \"$SUB_BREAK\"; \
        rm \"$DESC_FILE\"; \
        echo \"🗑️  Temporary description file '$DESC_FILE' has been removed.\"; \
      else \
        echo \"${RED}❌ Commit failed!${NC}\"; \
        echo \"$LINE_BREAK\"; \
        echo \"📄 Temporary file '$DESC_FILE' was preserved.\"; \
      fi; \
      return $COMMIT_STATUS; \
    else \
      if [ -n \"$DESC_FILE\" ]; then \
        echo \"${YELLOW}⚠️ \\\"$DESC_FILE\\\" not found. Multiline commit description wasn't included.${NC}\"; \
      fi; \
      git commit -m \"$COMMIT_TITLE\"; \
      COMMIT_STATUS=$?; \
      if [ $COMMIT_STATUS -eq 0 ]; then \
        COMMIT_HASH=$(git rev-parse --short HEAD); \
        echo \"${GREEN}✅ Commit successful! Created commit $COMMIT_HASH${NC}\"; \
        echo \"$LINE_BREAK\"; \
        echo \"📝 Message: $COMMIT_TITLE\"; \
        echo \"$SUB_BREAK\"; \
        echo \"🔄 Files changed:\"; \
        echo \"$(git diff --stat HEAD~1 HEAD | grep -v 'files changed' | sed 's/^  / /')\"; \
        if [ -n \"$DESC_FILE\" ]; then \
          echo \"$SUB_BREAK\"; \
          echo \"${YELLOW}⚠️ \\\"$DESC_FILE\\\" not found. Multiline commit description wasn't included.${NC}\"; \
        fi; \
      else \
        echo \"${RED}❌ Commit failed!${NC}\"; \
        echo \"$LINE_BREAK\"; \
        echo \"Please check your repository status and try again.\"; \
      fi; \
      return $COMMIT_STATUS; \
    fi; \
  }; f"

#### Git Multi-Line Commit Message

```ini
[alias]
  # Multi-line commit with message
  mcm = "!f() { \
    COMMIT_MSG=\"$1\"; \
    COMMIT_REGEX='^(feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert|hotfix|release)(\\([a-z0-9-]+\\))?: .+$'; \
    if ! [[ $COMMIT_MSG =~ $COMMIT_REGEX ]]; then \
      echo \"ERROR: Commit message does not follow conventional commits\"; \
      echo '=========================================================='; \
      echo \"📝 Format: type(scope): description\"; \
      echo \"👉 Examples: \\\"feat(auth): add login button\\\", \\\"fix: resolve null pointer exception\\\"\"; \
      echo \"✅ Valid types: feat, fix, docs, style, refactor, test, chore, perf, build, ci, revert, hotfix, release\"; \
      return 1; \
    fi; \
    echo \"$COMMIT_MSG\" > .git/COMMIT_EDITMSG && \
    git commit -F .git/COMMIT_EDITMSG; \
  }; f"
```

### Git Info

#### Git Super Status

`git s-status` shows the repository status, staged changes, unstaged changes, untracked files, and recent commits. You can include arguments to adjust the number of recent commits or to show verbose output e.g.:

```ini
[alias]
  # Super Status: Display status, recent commits, and staged changes

s-status = "!f() { \
  echo ''; \
  echo '== BRANCH INFO ℹ️  ======================'; \
  echo ''; \
  git branch -vv; \
  echo ''; \
  echo '== RECENT COMMITS 🕒 ======================'; \
  echo ''; \
  git log --oneline --graph --all --decorate -n 10; \
  echo ''; \
  echo '== LAST COMMIT CHANGES 📝 ================='; \
  echo ''; \
  git show --name-status --oneline HEAD | grep -v '^[0-9a-f]\\+ ' | sed 's/^/  /'; \
  echo ''; \
  echo '== STAGED CHANGES 🟦 ======================'; \
  echo ''; \
  git diff --staged --stat | sed 's/^/ /'; \
  echo ''; \
  echo '== UNSTAGED CHANGES 🟨 ===================='; \
  echo ''; \
  git diff --stat | sed 's/^/ /'; \
  echo ''; \
  echo '== UNTRACKED FILES 🔲 ====================='; \
  echo ''; \
  git ls-files --others --exclude-standard | sed 's/^/  /'; \
  echo ''; \
  echo '== SUMMARY 📊 ============================='; \
  echo ''; \
  staged=$(git diff --staged --name-only | wc -l | tr -d ' '); \
  unstaged=$(git diff --name-only | wc -l | tr -d ' '); \
  untracked=$(git ls-files --others --exclude-standard | wc -l | tr -d ' '); \
  branch=$(git rev-parse --abbrev-ref HEAD); \
  commits_ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0); \
  commits_behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0); \
  echo \"🌿 Branch: $branch\"; \
  echo \"📦 Changes: $staged staged, $unstaged unstaged, $untracked untracked\"; \
  echo \"🔄 Commits: $commits_ahead ahead, $commits_behind behind\"; \
}; f"
```

#### Git Super Diff

`git s-diff` shows the repository status, staged changes, unstaged changes, untracked files, and recent commits. You can include arguments to adjust the number of recent commits or to show verbose output e.g.

```ini
[alias]
  # Super Diff: Display status, diff, and staged diff
  s-diff = "!f() { \
    echo ''; \
    echo '== BRANCH INFO ℹ️  ======================'; \
    echo ''; \
    git branch -vv; \
    echo ''; \
    echo '== STAGED CHANGES 🟦 ======================'; \
    echo ''; \
    git diff --staged | sed 's/^/ /'; \
    echo ''; \
    echo '== UNSTAGED CHANGES 🟨 ===================='; \
    echo ''; \
    git diff --stat | sed 's/^/ /'; \
    echo ''; \
    echo '== SUMMARY 📊 ============================='; \
    echo ''; \
    staged=$(git diff --staged --name-only | wc -l | tr -d ' '); \
    unstaged=$(git diff --name-only | wc -l | tr -d ' '); \
    untracked=$(git ls-files --others --exclude-standard | wc -l | tr -d ' '); \
    branch=$(git rev-parse --abbrev-ref HEAD); \
    commits_ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0); \
    commits_behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0); \
    echo \"🌿 Branch: $branch\"; \
    echo \"📦 Changes: $staged staged, $unstaged unstaged, $untracked untracked\"; \
    echo \"🔄 Commits: $commits_ahead ahead, $commits_behind behind\"; \
  }; f"
```

## Appendix

### Core Git Commands

- `git init` - Initialize a new git repository
  - `git init --bare` - Create a bare repository with no working directory
  - `git init --template=<dir>` - Use custom directory as template for repository
- `git clone` - Clone an existing repository
  - `git clone --depth=<depth>` - Create a shallow clone with limited history
  - `git clone --branch=<branch>` - Clone a specific branch
  - `git clone --mirror` - Create a mirror repository
- `git config` - Configure git settings
  - `git config --global` - Set configuration for all repositories
  - `git config --local` - Set configuration for current repository
  - `git config --list` - List all configuration settings
- `git status` - Check the status of files in the working directory
  - `git status -s` - Display status in short format
  - `git status -b` - Show branch information
- `git diff` - Show changes between working directory and staging area
  - `git diff --staged` - Show changes between staging area and last commit
  - `git diff <commit>` - Show changes between working directory and specific commit
  - `git diff --name-only` - Show only names of changed files
- `git add` - Add files to the staging area
  - `git add -p` - Interactively add parts of files
  - `git add -u` - Add all modified tracked files
  - `git add .` - Add all changes in the current directory
- `git commit` - Commit staged changes to the repository
  - `git commit -m "<message>"` - Commit with a message
  - `git commit -a` - Automatically stage all modified tracked files
  - `git commit --amend` - Modify the last commit
- `git log` - View commit history
  - `git log --oneline` - Show each commit on a single line
  - `git log --graph` - Show commit history as a graph
  - `git log -p` - Show patches (changes) for each commit
- `git branch` - List, create, or delete branches
  - `git branch <name>` - Create a new branch
  - `git branch -d <name>` - Delete a branch
  - `git branch -a` - List all branches (local and remote)
- `git checkout` - Switch branches or restore files
  - `git checkout -b <name>` - Create and switch to a new branch
  - `git checkout -- <file>` - Discard changes in working directory
  - `git checkout <commit>` - Switch to a specific commit
- `git merge` - Merge changes from one branch into another
  - `git merge --no-ff` - Create a merge commit even if fast-forward is possible
  - `git merge --abort` - Abort the current merge process
  - `git merge --squash` - Squash all commits into a single commit
- `git pull` - Fetch and merge changes from a remote repository
  - `git pull --rebase` - Rebase local changes on top of fetched changes
  - `git pull --no-commit` - Fetch and merge but don't commit the result
  - `git pull --ff-only` - Only allow fast-forward merges
  - `git pull --autostash` - Automatically stash/unstash changes during pull
- `git push` - Push local changes to a remote repository
  - `git push -u origin <branch>` - Push and set upstream branch
  - `git push --force` - Force push (use with caution)
  - `git push --force-with-lease` - Safer force push that checks for upstream changes
  - `git push --tags` - Push all tags to remote
- `git fetch` - Download objects and refs from a remote repository
  - `git fetch --all` - Fetch from all remotes
  - `git fetch --prune` - Remove remote-tracking branches that no longer exist
  - `git fetch <remote> <branch>` - Fetch a specific branch
- `git remote` - Manage remote repositories
  - `git remote add <name> <url>` - Add a new remote
  - `git remote -v` - List all remotes with URLs
  - `git remote remove <name>` - Remove a remote
- `git stash` - Temporarily save changes that are not ready to be committed
  - `git stash save "<message>"` - Stash changes with a message (old syntax)
  - `git stash push -m "<message>"` - Stash changes with a message (new syntax)
  - `git stash list` - List all stashes
  - `git stash apply` - Apply the most recent stash
  - `git stash pop` - Apply and remove the most recent stash
- `git tag` - Create, list, delete, or verify tags
  - `git tag <name>` - Create a lightweight tag
  - `git tag -a <name> -m "<message>"` - Create an annotated tag
  - `git tag -d <name>` - Delete a tag
- `git mv` - Move or rename a file, directory, or symlink
  - `git mv <source> <destination>` - Move/rename a file
  - `git mv -f <source> <destination>` - Force move even if destination exists
- `git rm` - Remove files from the working tree and from the index
  - `git rm <file>` - Remove a file from working tree and index
  - `git rm --cached <file>` - Remove a file from index only
  - `git rm -r <directory>` - Recursively remove a directory

### Advanced Commands

- `git reset` - Reset current HEAD to the specified state
  - `git reset --soft <commit>` - Reset HEAD but keep changes staged
  - `git reset --mixed <commit>` - Reset HEAD and staging area but keep working directory
  - `git reset --hard <commit>` - Reset HEAD, staging area, and working directory
- `git rebase` - Reapply commits on top of another base tip
  - `git rebase -i <commit>` - Interactive rebase for editing commits
  - `git rebase --continue` - Continue rebase after resolving conflicts
  - `git rebase --abort` - Abort the current rebase operation
  - `git rebase --onto <newbase> <oldbase> <branch>` - Rebase branch onto new base
- `git cherry-pick` - Apply changes from specific commits to the current branch
  - `git cherry-pick <commit>` - Apply a single commit
  - `git cherry-pick <commit1>..<commit2>` - Apply a range of commits
  - `git cherry-pick --continue` - Continue cherry-pick after resolving conflicts
- `git bisect` - Binary search through commit history to find bugs
  - `git bisect start` - Start a bisect session
  - `git bisect good` - Mark current commit as good
  - `git bisect bad` - Mark current commit as bad
  - `git bisect reset` - End bisect session and return to original HEAD
- `git clean` - Remove untracked files from working directory
  - `git clean -n` - Show what would be removed (dry run)
  - `git clean -f` - Force removal of untracked files
  - `git clean -d` - Remove untracked directories
  - `git clean -x` - Remove ignored files too
- `git worktree` - Manage multiple working trees
  - `git worktree add <path> <branch>` - Create new working tree
  - `git worktree list` - List details of each working tree
  - `git worktree remove <path>` - Remove a working tree
- `git reflog` - Manage reflog information
  - `git reflog show` - Show log of reference updates
  - `git reflog delete` - Delete reflog entries
  - `git reflog expire` - Remove old reflog entries
- `git switch` - Switch branches (modern replacement for checkout)
  - `git switch <branch>` - Switch to an existing branch
  - `git switch -c <branch>` - Create and switch to a new branch
  - `git switch -` - Switch to the previous branch
- `git restore` - Restore working tree files (modern replacement for checkout)
  - `git restore <file>` - Restore file in working directory from HEAD
  - `git restore --source=<commit> <file>` - Restore file from specific commit
  - `git restore --staged <file>` - Unstage a file
- `git submodule` - Initialize, update, or inspect submodules
  - `git submodule add <repository> <path>` - Add a submodule
  - `git submodule init` - Initialize submodules
  - `git submodule update` - Update submodules
  - `git submodule foreach <command>` - Run command on each submodule
- `git revert` - Create a new commit that undoes changes from a previous commit
  - `git revert <commit>` - Revert specified commit
  - `git revert --no-commit <commit>` - Revert but don't create a commit
  - `git revert --continue` - Continue revert after resolving conflicts
- `git filter-branch` - Rewrite branches (use with caution, consider git-filter-repo instead)
  - `git filter-branch --tree-filter <command>` - Run command on each checked out tree
  - `git filter-branch --index-filter <command>` - Run command on each index
  - `git filter-branch --env-filter <command>` - Modify commit metadata
- `git am` - Apply a series of patches from a mailbox
  - `git am <mbox>` - Apply patches from mbox
  - `git am --abort` - Abort the current am operation
  - `git am --continue` - Continue after resolving conflicts
- `git format-patch` - Prepare patches for email submission
  - `git format-patch <since>` - Create patches from commits
  - `git format-patch -o <dir>` - Output patches to specified directory
  - `git format-patch --cover-letter` - Generate a cover letter
- `git apply` - Apply a patch to files and/or to the index
  - `git apply <patch>` - Apply patch
  - `git apply --check <patch>` - Check if patch can be applied cleanly
  - `git apply --stat <patch>` - Show statistics about patch
- `git bundle` - Move objects and refs by archive
  - `git bundle create <file> <git-rev-list-args>` - Create a bundle
  - `git bundle verify <file>` - Check if a bundle is valid
  - `git bundle list-heads <file>` - List references in a bundle
- `git rerere` - Reuse recorded resolution of conflicted merges
  - `git rerere status` - Show current status of recorded resolutions
  - `git rerere diff` - Show current conflicts and recorded resolutions

### Utility Commands

- `git show` - Show various types of objects
  - `git show <commit>` - Show commit and its changes
  - `git show --name-only` - Only display changed file names
  - `git show <tag>` - Show tag information
  - `git show <branch>` - Show last commit on branch
- `git blame` - Show what revision and author last modified each line of a file
  - `git blame <file>` - Show line-by-line authorship
  - `git blame -L <start>,<end> <file>` - Limit blame to specific lines
  - `git blame -w` - Ignore whitespace changes
- `git grep` - Print lines matching a pattern in tracked files
  - `git grep <pattern>` - Search for pattern in tracked files
  - `git grep -n <pattern>` - Show line numbers
  - `git grep --count <pattern>` - Show number of matches per file
- `git archive` - Create an archive of files from a named tree
  - `git archive --format=<fmt> <branch>` - Create archive in specified format
  - `git archive --output=<file> <branch>` - Output to a file
- `git shortlog` - Summarize git log output
  - `git shortlog -n` - Sort by number of commits
  - `git shortlog -s` - Show only commit count and author
  - `git shortlog -e` - Show email address of each author
- `git describe` - Give an object a human-readable name based on available ref
  - `git describe <commit>` - Describe a commit
  - `git describe --tags` - Use only tags to name the commit
- `git difftool` - Show changes using common diff tools
  - `git difftool <commit>` - Compare working tree with commit
  - `git difftool --tool=<tool>` - Use specified diff tool
  - `git difftool --dir-diff` - Compare directories instead of files
- `git mergetool` - Run merge conflict resolution tools
  - `git mergetool <file>` - Run merge tool on specified file
  - `git mergetool --tool=<tool>` - Use specified merge tool
- `git help` - Display help information about Git
  - `git help <command>` - Show help for specific command
  - `git help -a` - List all available commands
  - `git help -g` - List available guides
- `git rev-parse` - Pick out and massage parameters
  - `git rev-parse --show-toplevel` - Show the path of the top-level directory
  - `git rev-parse --abbrev-ref HEAD` - Show the current branch name
  - `git rev-parse <commit>` - Convert commit reference to SHA-1
- `git ls-files` - Show information about files in the index and working tree
  - `git ls-files --modified` - Show modified files
  - `git ls-files --others` - Show untracked files
  - `git ls-files --ignored` - Show ignored files
- `git ls-remote` - List references in a remote repository
  - `git ls-remote <repository>` - List references in specified repository
  - `git ls-remote --tags <repository>` - List only tags
- `git ls-tree` - List the contents of a tree object
  - `git ls-tree <tree-ish>` - List contents of a tree object
  - `git ls-tree -r <tree-ish>` - Recurse into subtrees
- `git request-pull` - Generate a summary of pending changes
  - `git request-pull <start> <url> [<end>]` - Generate pull request summary

### Miscellaneous Commands

- `git cat-file` - Provide content or type information for repository objects
  - `git cat-file -t <object>` - Show object type
  - `git cat-file -p <object>` - Pretty-print object content
  - `git cat-file -s <object>` - Show object size
- `git notes` - Add or inspect object notes
  - `git notes add -m "<message>" <object>` - Add note to object
  - `git notes remove <object>` - Remove notes from object
  - `git notes list` - List all notes
- `git prune` - Prune all unreachable objects from the object database
  - `git prune --expire <time>` - Prune objects older than specified time
  - `git prune --dry-run` - Show what would be pruned without removing
- `git verify-commit` - Check the GPG signature of commits
  - `git verify-commit <commit>` - Verify signature of specified commit
- `git verify-tag` - Check the GPG signature of tags
  - `git verify-tag <tag>` - Verify signature of specified tag
- `git merge-base` - Find as good common ancestors as possible for a merge
  - `git merge-base <commit1> <commit2>` - Find common ancestor
  - `git merge-base --all <commit1> <commit2>` - Find all common ancestors
- `git count-objects` - Count unpacked objects and their disk consumption
  - `git count-objects -v` - Show detailed statistics
  - `git count-objects -H` - Show sizes in human-readable format
- `git interpret-trailers` - Add or parse commit message trailers
  - `git interpret-trailers --in-place <file>` - Edit file in place
  - `git interpret-trailers --parse` - Parse trailers from stdin
- `git send-email` - Send a collection of patches as emails
  - `git send-email <patches>` - Send patches as emails
  - `git send-email --to=<recipient>` - Specify recipient
- `git instaweb` - Instantly browse your working repository in gitweb
  - `git instaweb --start` - Start web server with gitweb
  - `git instaweb --stop` - Stop web server
  - `git instaweb --browser=<browser>` - Specify browser to use
- `git bugreport` - Collect information for user to file a bug report
  - `git bugreport` - Generate a bug report file
- `git credential` - Retrieve and store user credentials
  - `git credential fill` - Fill in missing credentials
  - `git credential approve` - Approve valid credentials
  - `git credential reject` - Reject invalid credentials
- `git check-ignore` - Debug gitignore / exclude files
  - `git check-ignore <path>` - Check if path is ignored
  - `git check-ignore -v <path>` - Show which pattern caused path to be ignored
- `git check-attr` - Display gitattributes information
  - `git check-attr <attribute> <file>` - Check attribute for file
  - `git check-attr --all <file>` - List all attributes for file
- `git check-mailmap` - Show canonical names and email addresses of contacts
  - `git check-mailmap <email>` - Show canonical name for email address
- `git gc` - Cleanup unnecessary files and optimize the local repository
  - `git gc --aggressive` - More aggressively optimize the repository
  - `git gc --prune=<date>` - Prune loose objects older than date
- `git fsck` - Verify the connectivity and validity of objects in the database
  - `git fsck --full` - Check all objects
  - `git fsck --no-dangling` - Skip reporting dangling objects

### Common Flags, Filters, and Variables

#### Flags

- `--verbose` or `-v` - Provide more detailed output
  - Use with: `git clone`, `git fetch`, `git merge`, `git pull`, `git push`, `git status`, `git commit`
  - Example: `git push -v origin main`
- `--quiet` or `-q` - Suppress output
  - Use with: `git clone`, `git fetch`, `git merge`, `git pull`, `git push`, `git add`
  - Example: `git pull -q origin`
- `--dry-run` or `-n` - Show what would be done without actually doing it
  - Use with: `git clean`, `git add`, `git rm`, `git merge`, `git push`
  - Example: `git clean -n`
- `--all` or `-a` - Operate on all items
  - Use with: `git branch`, `git fetch`, `git pull`, `git push`, `git commit`
  - Example: `git branch -a` (list all branches including remote)
- `--force` or `-f` - Force an operation that might otherwise be prevented
  - Use with: `git push`, `git branch`, `git clean`, `git checkout`, `git reset`
  - Example: `git push -f origin main` (force push, use with caution)
- `--patch` or `-p` - Show changes in patch format
  - Use with: `git log`, `git show`, `git diff`, `git add`
  - Example: `git add -p` (interactively stage changes)
- `--stat` - Show statistics about changes
  - Use with: `git log`, `git show`, `git diff`
  - Example: `git log --stat` (show commit history with file statistics)

#### Filters

- `--author=<pattern>` - Filter by author
  - Use with: `git log`, `git shortlog`, `git blame`
  - Example: `git log --author="John Doe"`
- `--since=<date>`, `--after=<date>` - Filter by date (after)
  - Use with: `git log`, `git diff`, `git shortlog`
  - Example: `git log --since="2 weeks ago"`
- `--until=<date>`, `--before=<date>` - Filter by date (before)
  - Use with: `git log`, `git diff`, `git shortlog`
  - Example: `git log --until="yesterday"`
- `--grep=<pattern>` - Filter by commit message pattern
  - Use with: `git log`, `git show`, `git shortlog`
  - Example: `git log --grep="fix bug"`
- `--path=<path>` - Filter by file path
  - Use with: `git log`, `git diff`
  - Example: `git log -- path/to/file.js`

#### Reference Variables

- `HEAD` - Reference to the current commit
  - Use with: `git show`, `git reset`, `git diff`, `git checkout`
  - Example: `git show HEAD` (show the current commit)
- `HEAD~n` - Reference to the nth ancestor of HEAD
  - Use with: `git show`, `git reset`, `git diff`, `git checkout`
  - Example: `git reset HEAD~3` (reset to 3 commits back)
- `<branch>^` - Reference to the parent of the tip of the branch
  - Use with: `git show`, `git reset`, `git diff`, `git checkout`
  - Example: `git show main^` (show the parent of the tip of main)
- `<branch>~n` - Reference to the nth ancestor of the branch
  - Use with: `git show`, `git reset`, `git diff`, `git checkout`
  - Example: `git checkout feature~2` (checkout 2 commits back from feature branch)
- `<commit>^n` - Reference to the nth parent of a merge commit
  - Use with: `git show`, `git reset`, `git diff`, `git checkout`
  - Example: `git show HEAD^2` (show the second parent of a merge commit)
- `<commit>:<path>` - Reference to a file at a specific commit
  - Use with: `git show`, `git diff`
  - Example: `git show HEAD~3:path/to/file.js` (show file 3 commits back)
- `@{upstream}` or `@{u}` - Reference to the upstream branch
  - Use with: `git merge`, `git rebase`, `git diff`, `git log`
  - Example: `git merge @{u}` (merge from upstream branch)

#### Other

- `--` - Separator between options and file paths
  - Use with: `git checkout`, `git diff`, `git log`
  - Example: `git checkout -- file.txt` (restore file from HEAD)