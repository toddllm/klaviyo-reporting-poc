# Branch Cleanup Utility

This utility helps identify and clean up branches that have already been merged via Pull Requests but haven't been deleted yet.

## Features

- Identifies local branches with merged PRs
- Identifies remote branches with merged PRs
- Provides an interactive prompt to safely delete identified branches
- Prevents deletion of the currently checked out branch

## Usage

```bash
# Run the script from the repository root
./cleanup_branches.py
```

## How It Works

1. The script fetches all PRs from GitHub using the GitHub CLI
2. It identifies local and remote branches in your repository
3. It matches branches to merged PRs
4. It displays branches that can be safely deleted
5. It prompts for confirmation before deleting any branches

## Requirements

- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated
- Git command-line tools

## Best Practices

- Run this script periodically to keep your repository clean
- Always review the list of branches before confirming deletion
- Make sure you're not actively working on any of the branches that will be deleted
