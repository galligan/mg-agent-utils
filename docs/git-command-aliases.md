# Git Command Aliases

This is a collection of git command aliases that I use in conjunction with AI Agents to streamline their git workflow.

## Aliases

- `git sda` [🔗](#add--stage-git-sda) - Add files to the staging area and show the status of the repository.
- `git sdc` [🔗](#conventional-commit-git-sdc) - Create a conventional commit with optional multi-line description.
- `git sdsc` [🔗](#split-commit-with-message-git-sdsc) - Split changes into multiple conventional commits.
- `git sd-diff` [🔗](#super-duper-diff-git-sd-diff) - Display detailed status, diff, and staged diff information.
- `git sd-status` [🔗](#super-duper-status-git-sd-status) - Display comprehensive repository status with branch analysis.
- `git sd-push` [🔗](#super-duper-push-git-sd-push) - Smart push command with safety checks and detailed feedback.
- `git sd-branch` [🔗](#super-duper-branch-git-sd-branch) - Smart branch management with best practices enforcement.

## Adding these aliases to your `gitconfig`

Follow these steps to add these powerful aliases to your Git configuration using the include path method:

### Include the aliases file in your gitconfig

This method keeps aliases in a separate file, making them easier to update and manage.

#### Step 1: Create your Git config directory (if it doesn't exist)

~~~bash
# Create the Git config directory if it doesn't exist
mkdir -p ~/.config/git
~~~

#### Step 2: Download the aliases file

~~~bash
# Download the aliases file to your Git config directory
curl -o ~/.config/git/sd-aliases.ini https://raw.githubusercontent.com/yourusername/yourrepo/main/src/gitconfig-aliases.ini

# Or if you've cloned the repository locally
cp /path/to/repo/src/gitconfig-aliases.ini ~/.config/git/sd-aliases.ini
~~~

#### Step 3: Add the include directive to your gitconfig

~~~bash
# Add an include directive to your gitconfig
git config --global --add include.path ~/.config/git/sd-aliases.ini
~~~

#### Step 4: Verify the installation

~~~bash
# Check if the aliases are available
git sd-status --help

# Or list all available aliases
git config --get-regexp alias
~~~

> 💡 **Tip:** The include directive keeps your aliases separate from your main config, making it easier to update them in the future. When new versions of the aliases are released, you only need to update the aliases.ini file.

### Troubleshooting Installation

If you encounter any issues with the installation:

1. **Aliases not found:** Make sure the file path in the include directive is correct.

   ~~~bash
   # Check your current Git configuration
   git config --list
   ~~~

2. **Permission issues:** Ensure you have write permissions to the Git config directory and files.

3. **Syntax errors:** If Git reports syntax errors, check your .gitconfig file for any malformed entries.

   ~~~bash
   # Validate your Git config syntax
   git config --list --show-origin
   ~~~

4. **Path issues on Windows:** On Windows, use forward slashes or escaped backslashes in file paths.

   ~~~bash
   # Windows example
   git config --global --add include.path C:/Users/username/.config/git/sd-aliases.ini
   ~~~

### Customizing the aliases

Once installed, you can customize any alias by editing the included file: `~/.config/git/sd-aliases.ini`

For example, to modify the `git sda` command:

~~~bash
git config --global alias.sda '!f() { git add "$@" && echo "=== Custom Message ==="; git status --short | cat; }; f'
~~~

## Super Duper Add & Stage (`git sda`)

- **Command**: `git sda`
- **Description**: Add files to the staging area and show the status of the repository.
- **Steps**:
  - Add files to the staging area.
  - Show the status of the repository.
  - Show the changes that are staged.

### `git sda` in `gitconfig`

~~~ini
[alias]
  sda = "!f() { \
    git add \"$@\" && \
    echo '=== 🚦 REPOSITORY STATUS AFTER ADD ==='; \
    git status --short | cat; \
    echo '\n=== 🔵 STAGED CHANGES ==='; \
    git diff --staged --color | cat; \
  }; f"
~~~

### Example Input/Output

~~~bash
$ git sda src/auth.js src/components/LoginForm.js

=== 🚦 REPOSITORY STATUS AFTER ADD ===
M  src/auth.js
A  src/components/LoginForm.js
?? src/components/SignupForm.js
 M src/styles/main.css

=== 🔵 STAGED CHANGES ===
diff --git a/src/auth.js b/src/auth.js
index 8ea9f3a..2b5d8c2 100644
--- a/src/auth.js
+++ b/src/auth.js
@@ -42,7 +42,15 @@ class AuthService {
   }
 
   async login(username, password) {
-    // Implementation
+    try {
+      const response = await this.api.post('/login', { username, password });
+      this.setToken(response.data.token);
+      this.setUser(response.data.user);
+      return { success: true, user: response.data.user };
+    } catch (error) {
+      console.error('Login failed:', error.message);
+      return { success: false, error: error.message };
+    }
   }
 }
 
diff --git a/src/components/LoginForm.js b/src/components/LoginForm.js
new file mode 100644
index 0000000..5a3df2e
--- /dev/null
+++ b/src/components/LoginForm.js
@@ -0,0 +1,45 @@
+import React, { useState } from 'react';
+import { useAuth } from '../hooks/useAuth';
+
+const LoginForm = ({ onSuccess }) => {
+  const [username, setUsername] = useState('');
+  const [password, setPassword] = useState('');
+  const [loading, setLoading] = useState(false);
+  const [error, setError] = useState('');
+  const { login } = useAuth();
+
+  const handleSubmit = async (e) => {
+    e.preventDefault();
+    setLoading(true);
+    setError('');
+
+    try {
+      const result = await login(username, password);
+      if (result.success) {
+        onSuccess && onSuccess(result.user);
+      } else {
+        setError(result.error || 'Login failed');
+      }
+    } catch (err) {
+      setError('An unexpected error occurred');
+    } finally {
+      setLoading(false);
+    }
+  };
+
+  return (
+    <form onSubmit={handleSubmit}>
+      {error && <div className="error">{error}</div>}
+      <input
+        type="text" value={username} placeholder="Username"
+        onChange={(e) => setUsername(e.target.value)} required />
+      <input
+        type="password" value={password} placeholder="Password"
+        onChange={(e) => setPassword(e.target.value)} required />
+      <button type="submit" disabled={loading}>
+        {loading ? 'Logging in...' : 'Log In'}
+      </button>
+    </form>
+  );
+};
+
+export default LoginForm;
~~~

> 💡 This example shows adding multiple files at once. Note how the status shows both staged files (prefixed with 'M' and 'A') and unstaged files (prefixed with '??' and ' M'). The diff output shows the actual code changes in detail.

## Super Duper Commit (`git sdc`)

- **Command**: `git sdc <message> [description-file]`
- **Description**: Create a commit using conventional commit format with optional multi-line description from a file.
- **Features**:
  - Enforces conventional commit format
  - Supports multi-line commit messages via description file
  - Validates commit message length
  - Shows detailed commit summary
  - Auto-removes description file after successful commit

### Example Input/Output

~~~bash
# Simple conventional commit:
$ git sdc "feat(auth): add login functionality"

✅ Commit successful! Created commit 7a2e9c4
==============================================================
📝 Message: feat(auth): add login functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
🔄 Files changed:
 src/auth.js            | 10 ++++++++--
 src/components/LoginForm.js | 45 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 53 insertions(+), 2 deletions(-)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# With multi-line description file:
> cat > COMMIT_DESC.tmp
This implements the login functionality with the following features:
- Username/password authentication
- Error handling and validation
- Loading state management
- Proper API integration with error handling

BREAKING CHANGE: The auth API now requires a valid CSRF token for all requests.
Closes #123
$ git sdc "feat(auth): add login functionality" COMMIT_DESC.tmp

✅ Commit successful! Created commit 8f4d2e7
==============================================================
📝 Message: feat(auth): add login functionality

This implements the login functionality with the following features:
- Username/password authentication
- Error handling and validation
- Loading state management
- Proper API integration with error handling

BREAKING CHANGE: The auth API now requires a valid CSRF token for all requests.
Closes #123
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
🔄 Files changed:
 src/auth.js            | 10 ++++++++--
 src/components/LoginForm.js | 45 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 53 insertions(+), 2 deletions(-)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
🗑️ Temporary description file 'COMMIT_DESC.tmp' has been removed.
~~~

> 💡 This example shows both a simple commit and a commit with a detailed description file that includes breaking changes and issue references, showing the full conventional commit format.

## Super Duper Split Commit (`git sdsc`)

- **Command**: `git sdsc <files-1> <message-1> [<files-2> <message-2> ...]`
- **Description**: Split staged changes into multiple conventional commits.
- **Features**:
  - Supports multiple commit groups
  - Validates all commit messages
  - Shows detailed progress and results
  - Handles file patterns and specific files
  - Provides comprehensive summary

### Example Input/Output

~~~bash
$ git sdsc "src/auth.js" "feat(auth): implement login logic" "src/components/LoginForm.js" "feat(ui): create login form component" "src/styles/auth.css" "style: add login form styling"

=========================================
      ✨ SUPER DUPER SPLIT COMMIT ✨
=========================================
📋 Split plan:
 - Group 1: src/auth.js → feat(auth): implement login logic
 - Group 2: src/components/LoginForm.js → feat(ui): create login form component
 - Group 3: src/styles/auth.css → style: add login form styling

🔍 Processing Group 1...
 - Adding: src/auth.js
 - Creating commit: feat(auth): implement login logic
✅ Created commit a1b2c3d: feat(auth): implement login logic

🔍 Processing Group 2...
 - Adding: src/components/LoginForm.js
 - Creating commit: feat(ui): create login form component
✅ Created commit e4f5g6h: feat(ui): create login form component

🔍 Processing Group 3...
 - Adding: src/styles/auth.css
 - Creating commit: style: add login form styling
✅ Created commit i7j8k9l: style: add login form styling

✅ Split complete! Created 3 commits:
 - a1b2c3d: feat(auth): implement login logic
 - e4f5g6h: feat(ui): create login form component
 - i7j8k9l: style: add login form styling
~~~

> 💡 This example shows splitting changes to multiple files into separate logical commits, each with its own conventional commit message. You can provide as many file-message pairs as needed, making it perfect for organizing large changes into atomic commits.

## Super Duper Diff (`git sd-diff`)

- **Command**: `git sd-diff`
- **Description**: Enhanced diff command showing repository status, staged and unstaged changes.
- **Features**:
  - Shows branch information
  - Displays staged changes
  - Shows unstaged changes
  - Provides status summary

### Example Input/Output

~~~bash
$ git sd-diff

=========================================
         ✨ SUPER DUPER DIFF ✨
=========================================

ℹ️  Branch Info:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* feature/login-system 7a2e9c4 [origin/feature/login-system: behind 2] feat(auth): add login functionality

🟦 Staged Changes:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
diff --git a/src/hooks/useAuth.js b/src/hooks/useAuth.js
new file mode 100644
index 0000000..3c51d89
--- /dev/null
+++ b/src/hooks/useAuth.js
@@ -0,0 +1,32 @@
+import { useContext, createContext } from 'react';
+import { AuthService } from '../auth';
+
+const AuthContext = createContext(null);
+
+export const AuthProvider = ({ children }) => {
+  // Auth provider implementation
};

🟨 Unstaged Changes:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
diff --git a/src/components/LoginForm.js b/src/components/LoginForm.js
index 5a3df2e..b95a214 100644
--- a/src/components/LoginForm.js
+++ b/src/components/LoginForm.js
@@ -1,5 +1,6 @@
 import React, { useState } from 'react';
 import { useAuth } from '../hooks/useAuth';
+import { validateCredentials } from '../utils/validation';
 
 const LoginForm = ({ onSuccess }) => {
   const [username, setUsername] = useState('');

diff --git a/src/components/SignupForm.js b/src/components/SignupForm.js
new file mode 100644
index 0000000..4d8c91a
--- /dev/null
+++ b/src/components/SignupForm.js
@@ -0,0 +1,48 @@
+import React, { useState } from 'react';
+import { useAuth } from '../hooks/useAuth';
+// Signup form implementation
+
📊 Summary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- 1 file staged (new)
- 2 files unstaged (1 modified, 1 new)
- Branch is behind remote by 2 commits
- Working on feature branch: feature/login-system
~~~

> 💡 This detailed view shows not only the staged and unstaged changes, but also provides the current branch status including its relationship to the remote branch. The output clearly differentiates between new files, modifications, and includes relevant line numbers and context.

## Super Duper Status (`git sd-status`)

- **Command**: `git sd-status [history-depth]`
- **Description**: Comprehensive repository status with intelligent branch analysis and suggestions.
- **Features**:
  - Shows detailed branch relationships
  - Analyzes branch health
  - Provides workflow suggestions
  - Displays merge conflicts
  - Shows stashed changes
  - Configurable history depth

### Example Input/Output

~~~bash
$ git sd-status 3

=========================================
        ✨ SUPER DUPER STATUS ✨
=========================================

ℹ️  Branch Info:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* feature/login-system 7a2e9c4 [origin/feature/login-system: behind 2] feat(auth): add login functionality

📊 Repository Status:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Modified  : src/components/LoginForm.js
New       : src/components/SignupForm.js
Staged    : src/hooks/useAuth.js (new)
Untracked : src/utils/validation.js

📜 Recent Commits:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
7a2e9c4 feat(auth): add login functionality (HEAD -> feature/login-system)
 - src/auth.js            | 10 ++++++++--
 - src/components/LoginForm.js | 45 +++++++++++++++++++++++++++++++++++++++++++++
 
8f4d2e7 feat(api): add auth API endpoints (origin/feature/login-system)
 - src/api/endpoints.js    | 28 ++++++++++++++++++++++++++++
 - src/api/index.js        | 3  ++-

3d5e1f9 chore: update dependencies
 - package.json            | 5  ++---
 - yarn.lock               | 42 +++++++++++++++++++++++++++++++-----------

📊 Super Duper Status Summary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
🌿 Branch: [current] feature/login-system [+2, behind 2] ← dev [+5 -0] ← main
🚧 Working Status: 1 staged, 2 modified, 1 untracked
🔄 Sync Status: ⚠️ Your branch is behind by 2 commits

⚠️ Action Required:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Pull latest changes from origin/feature/login-system before pushing
* You have unstaged changes that need to be committed
* Consider running `git sda .` to stage all changes

💡 Suggested Next Steps:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Pull latest changes:     git pull origin feature/login-system
2. Stage all changes:       git sda .
3. Commit your changes:     git sdc "type(scope): description"
4. Push to remote:          git sd-push
~~~

> 💡 This example shows the comprehensive status output with a specified history depth (3 commits), including detailed information about uncommitted changes, branch relationships, and actionable recommendations. The output helps identify potential issues and provides clear next steps.

## Super Duper Push (`git sd-push`)

- **Command**: `git sd-push [--force]`
- **Description**: Smart push command with safety checks and comprehensive feedback.
- **Features**:
  - Validates branch status
  - Prevents accidental main/master pushes
  - Auto-handles new branches
  - Attempts auto-merge when possible
  - Shows detailed push summary
  - Provides next steps

### Example Input/Output

~~~bash
$ git sd-push

=========================================
          ✨ SUPER DUPER PUSH ✨
=========================================

🔍 Branch status:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Current branch: feature/login-system
Remote status: ✓ exists on origin
Local commits: 1 commit ahead of origin/feature/login-system
Remote commits: 0 commits behind origin/feature/login-system

🌿 Branch hierarchy:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main ← dev ← feature/login-system ✓

🔄 Push action:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pushing feature/login-system to origin/feature/login-system...
Counting objects: 5, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 742 bytes | 742.00 KiB/s, done.
Total 5 (delta 2), reused 0 (delta 0)
remote: Resolving deltas: 100% (2/2), completed with 1 local object.
To github.com:username/repo.git
   8f4d2e7..7a2e9c4  feature/login-system -> feature/login-system

✅ Push successful!

📋 Push Summary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• Pushed 1 commit to origin/feature/login-system
• HEAD is now at: 7a2e9c4 feat(auth): add login functionality

🔮 Next Steps:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• Create a pull request: https://github.com/username/repo/compare/dev...feature/login-system
• Continue working on feature/login-system
• Switch to another branch: git checkout <branch-name>
~~~

> 💡 This example shows a successful push operation with detailed information about the branch status before pushing, the actual push process, and suggested next steps after the push. The command provides contextual guidance based on the current state of the repository.

## Super Duper Branch (`git sd-branch`)

- **Command**: `git sd-branch [feature-branch-name]`
- **Description**: Smart branch management enforcing git-flow best practices.
- **Features**:
  - Enforces branch hierarchy (main → dev → feature)
  - Creates missing dev branch when needed
  - Validates branch relationships
  - Shows branch status and relationships
  - Provides workflow suggestions

### Example Input/Output

~~~bash
# Creating a new feature branch:
$ git sd-branch feature/user-registration

=========================================
        ✨ SUPER DUPER BRANCH ✨
=========================================

🔍 Current State:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Current branch: main
Main branch (main): ✓ exists
Dev branch (dev): ❌ missing

🚀 Action Plan:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Creating dev branch from main...
   git checkout -b dev main
   Switched to a new branch 'dev'
   
2. Creating feature branch from dev...
   git checkout -b feature/user-registration dev
   Switched to a new branch 'feature/user-registration'

✅ Branch Creation Complete:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Successfully created branch hierarchy:
main → dev → feature/user-registration

📋 Branch Summary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• You are now on: feature/user-registration
• Branched from: dev (new)
• Dev branched from: main
• Local branches: ✓ consistent with git-flow pattern
• Ready to work on: feature/user-registration

💡 Next Steps:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• Make your changes for user registration feature
• Use git sda to stage changes
• Commit with git sdc "feat(user): add registration"
• Push to remote with git sd-push

# Checking current branch status:
$ git sd-branch

=========================================
        ✨ SUPER DUPER BRANCH ✨
=========================================

🔍 Current State:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Current branch: feature/user-registration
Main branch (main): ✓ exists (0 commits ahead, 0 commits behind)
Dev branch (dev): ✓ exists (0 commits ahead, 0 commits behind main)

🌿 Branch Hierarchy:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• main (base branch)
  └── dev (development branch)
      └── feature/user-registration (current feature branch) ✓

📋 Branch Analysis:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• Branch naming: ✓ follows git-flow convention
• Branch hierarchy: ✓ properly structured
• Branch ancestry: ✓ feature branch is correctly based on dev
• No uncommitted changes

✅ Branch Status: Healthy
~~~

> 💡 These examples show both creating a new feature branch (automatically setting up the dev branch if needed) and checking the current branch status. The command enforces proper git-flow structure and provides detailed guidance on next steps based on the current state of the repository.
