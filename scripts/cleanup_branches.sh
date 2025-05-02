#!/bin/bash

# Script to clean up merged branches

# Get the current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Fetch the latest from remote
git fetch --prune

# Get list of merged branches (excluding main and current branch)
MERGED_BRANCHES=$(git branch --merged main | grep -v "^\*" | grep -v "main" | tr -d ' ')

# Get list of open PR branches from GitHub CLI
OPEN_PR_BRANCHES=$(gh pr list --state open --json headRefName --jq '.[].headRefName')

# Filter out branches with open PRs
BRANCHES_TO_DELETE=""
for BRANCH in $MERGED_BRANCHES; do
    if ! echo "$OPEN_PR_BRANCHES" | grep -q "$BRANCH"; then
        BRANCHES_TO_DELETE="$BRANCHES_TO_DELETE $BRANCH"
    fi
done

echo "The following branches have been merged into main and will be deleted:"
echo "$BRANCHES_TO_DELETE"
echo ""

# If no branches to delete, exit
if [ -z "$BRANCHES_TO_DELETE" ]; then
    echo "No merged branches to delete."
    exit 0
fi

# Confirm before proceeding
read -p "Do you want to proceed with deletion? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# Delete local branches
for BRANCH in $BRANCHES_TO_DELETE; do
    echo "Deleting local branch: $BRANCH"
    git branch -d "$BRANCH"
done

# Delete remote branches
for BRANCH in $BRANCHES_TO_DELETE; do
    echo "Deleting remote branch: $BRANCH"
    git push origin --delete "$BRANCH"
done

echo ""
echo "Branch cleanup completed."
