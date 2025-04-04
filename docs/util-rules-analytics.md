# 📈 Agent Utility - Rules Analytics

- **Source:**
  - [rules_analytics.py](.agent/utils/rules_analytics.py)
- **Use with:**
  - Any AI agent can use default rules and run terminal commands e.g. Cursor, Claude Code, Roo Code, etc.
- **Purpose:**
  - Tracks frequency usage of rules (e.g. `my-rule.mdc`)
  - By agent (Cursor, Roo Code, etc.)

## Table of Contents

- [How to use it](#how-to-use-it)
  - [Before you start](#before-you-start)
  - [Add the tracking prompt](#add-the-tracking-prompt)
- [What it does](#what-it-does)
  - [Track rule usage](#1-track-rule-usage-write)
  - [Read usage analytics](#2-read-usage-analytics-read)
  - [Rename rule](#3-rename-rule-rename)
- [How it works](#how-it-works)

## How to use it

### Before you start

1. Add the `rules_analytics.py` script to your project.
   - Put the script in a directory of your choice e.g.: `.agent/utils/rules_analytics.py`
2. Run the following command to make the script executable (replace `path/to/` with the actual path to the script):

```shell
chmod +x path/to/rules_analytics.py
```

3. Add the analytics data JSON file to your `.gitignore` to avoid committing the analytics data.

```gitignore
# Agent Utilities
rules_analytics.json
```

### Add the tracking prompt

Add the following prompt to your agent rules/configuration (be sure to replace `path/to/` with the actual path to the script):

````markdown
- Important: Any time you use a rule, run the following command with the parameters:
  - `filename` (string): The name and extension of the rule file you used e.g. `my-rule.mdc`
  - `by` (string): The name of the agent being used e.g. `Cursor, Roo Code, etc.`

  ```shell
  $ path/to/rules_analytics.py write --filename "<filename>" --by "<agent_name>"
  ```
````

**Where to add:**

- **Cursor:** `~/.cursorrules` or a `./cursor/rules/my-rule.mdc` file, configured with `alwaysApply: true`
- **Windsurf:** `~/.windsurfrules`
- **Roo Code/Cline:** `~/.clinerules`
- **Claude Code:** `~/Claude.md`

### Optional: Add prompts to read analytics/rename rules

Add the following prompts to your agent rules/configuration to read analytics and rename rules:

````markdown
- Important: Upon request for rule analytics, or renaming a rule within the analytics data, run the appropriate command:
  - `read`: `$ path/to/rules_analytics.py read [--sort {last,first,recent,name}] [--filter "<agent_name>"]`
  - `rename`: `$ path/to/rules_analytics.py rename <old_filename.mdc> <new_filename.mdc>`

````

## What it does

The utility supports three operations `write`, `read`, and `rename`:

### 1. Track rule usage (`write`)

This operation tracks when a rule file is used by an agent by writing to the analytics file.

#### Write command format

```shell
.agent/utils/rules_analytics.py write --filename "<filename>" --by "<agent_name>"
```

### 2. Read usage analytics (`read`)

This operation displays a formatted table of the usage analytics data.

#### Read command format

```shell
.agent/utils/rules_analytics.py read [--sort {last,first,recent,name}] [--filter "<agent_name>"]
```

#### Read parameters

- `--sort`: Sort the results by:
  - `last` or `recent` (default): Sort by last usage date (most recent first)
  - `first`: Sort by first usage date (oldest first)
  - `name`: Sort alphabetically by rule filename
- `--filter`: Filter results by agent name (fuzzy search)

#### Example read commands

```shell
# Show all rules sorted by most recently used
.agent/utils/rules_analytics.py read

# Show all rules sorted alphabetically by filename
.agent/utils/rules_analytics.py read --sort name

# Show rules used by Cursor (with fuzzy matching)
.agent/utils/rules_analytics.py read --filter cursor

# Show rules used by Roo Code sorted by first usage
.agent/utils/rules_analytics.py read --filter "roo code" --sort first
```

### 3. Rename Rule (`rename`)

This operation allows you to rename a rule while preserving its usage history. The old name is stored as a previous name, which is displayed in the read operation.

#### Rename command format

```shell
.agent/utils/rules_analytics.py rename <old_filename> <new_filename>
```

#### Rename parameters

- `old_filename`: The old filename of the rule (required, first argument)
- `new_filename`: The new filename of the rule (required, second argument)

#### Example rename commands

```shell
# Rename a rule file
.agent/utils/rules_analytics.py rename old-rules.mdc new-rules.mdc
```

#### Behavior

- If the old name doesn't exist in the analytics data, an error is displayed.
- If the new name already exists in the analytics data, the history from the old rule is merged with the new rule:
  - Usage counts from agents in both rules are summed
  - The earlier of the two first-use dates is kept
  - The later of the two last-use dates is kept
  - Previous names from both rules are combined
- Previous names are displayed in the read operation output

## How it works

The `rules_analytics.py` script tracks usage analytics for rule files. It manages a JSON file to store information about which rules are being used, by which agents, and how frequently.

### Write operation

Upon running the 'write' command, the script will:

1. Check if the `rules_analytics.json` file exists in the same directory as the script. If not, it will create a new one.
2. Read the existing data or create a new data structure if the file is corrupted.
3. Convert the agent name to kebab-case (lowercase with hyphens) for consistency.
4. Check if the rule file exists in the data. If not, it will add a new entry for the rule file.
5. Check if the agent exists in the usage dictionary for the rule file. If not, it will add a new entry for the agent with the current timestamp as `firstUsed`.
6. Increment the `usageCount` for the specified agent.
7. Update the `lastUsed` timestamp for the agent.
8. Write the updated data back to the file with proper formatting.

### Read operation

When using the 'read' command, the script will:

1. Load the analytics data from the JSON file.
2. Process the data to calculate total usage counts and find the most recent usage information.
3. Convert filter terms to kebab-case and apply fuzzy matching for filtering agents.
4. Sort the data according to the specified sort parameter.
5. Display a formatted table with columns for:
   - Filename
   - Total Usage Count
   - Last Agent
   - Last Used Date
   - Previous Names (if any rules have been renamed)

### Rename operation

When using the 'rename' command, the script will:

1. Check if the old rule name exists in the analytics data.
2. If the new name already exists, merge the usage data:
   - For each agent in the old rule's usage:
     - If the agent doesn't exist in the new rule, copy the usage data.
     - If the agent exists in both rules, combine the usage data (sum counts, keep earliest first use, keep latest last use).
   - Add the old name to the previous names list of the new rule.
   - Add any previous names from the old rule to the new rule's previous names list.
3. If the new name doesn't exist, create a new entry with the old rule's data and add the old name to its previous names list.
4. Remove the old rule entry from the analytics data.
5. Save the updated analytics data.

### Agent name normalization

All agent names are converted to kebab-case for consistent storage and retrieval:

- Spaces, underscores, and slashes are converted to hyphens
- All text is lowercased
- Special characters are removed except for `.` and `-`
- Multiple consecutive hyphens are consolidated into a single hyphen
- Example: "Roo Code Agent/2.0" becomes "roo-code-agent-2.0"

This makes filtering and comparing agent names more reliable.

### Timestamp format

All timestamps follow the ISO 8601 format: `YYYY-MM-DD[T]HH:MM:SS[Z]`

Example: `2025-04-04T14:43:24+00:00`

### Data structure

The analytics data is stored in a JSON file with an optimized dictionary-based structure:

```json
{
  "rules": {
    "example-rule.mdc": {
      "usage": {
        "cursor": {
          "usageCount": 5,
          "firstUsed": "2025-04-04T14:30:00+00:00",
          "lastUsed": "2025-04-04T15:45:00+00:00"
        },
        "roo-code": {
          "usageCount": 2,
          "firstUsed": "2025-04-05T09:15:00+00:00",
          "lastUsed": "2025-04-05T10:30:00+00:00"
        }
      },
      "previousNames": [
        "old-example-rule.mdc",
        "original-example-rule.mdc"
      ]
    }
  }
}
```

The data structure eliminates duplication by:

- Using filenames as keys in the rules dictionary (instead of storing them in each object)
- Using kebab-cased agent names as keys in the usage dictionary (instead of storing them in each object)
- Storing a list of previous names for each rule to track rename history

The utility will automatically migrate existing data to this optimized format.
