#!/bin/bash

# Script to clean up merged branches

# Get the current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Fetch the latest from remote
git fetch --prune

# Get list of merged branches (excluding main and current branch)
MERGED_BRANCHES=$(git branch --merged main | grep -v "^\*" | grep -v "main" | tr -d ' ')

echo "The following branches have been merged into main and will be deleted:"
echo "$MERGED_BRANCHES"
echo ""

# Confirm before proceeding
read -p "Do you want to proceed with deletion? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# Delete local branches
for BRANCH in $MERGED_BRANCHES; do
    echo "Deleting local branch: $BRANCH"
    git branch -d "$BRANCH"
done

# Delete remote branches
for BRANCH in $MERGED_BRANCHES; do
    echo "Deleting remote branch: $BRANCH"
    git push origin --delete "$BRANCH"
done

echo ""
echo "Branch cleanup completed."
