#!/bin/bash

# Custom script to clean up branches based on PR status

# Branches to keep (current branch and branches with open PRs)
KEEP_BRANCHES=(
  "feature/git-workflow-and-branch-cleanup"
  "feature/update-pr-plan-to-mark-pr3-complete"
  "main"
)

# Get all local branches
ALL_BRANCHES=$(git branch | grep -v "^\*" | tr -d ' ')

# Identify branches to delete
DELETE_BRANCHES=()
for BRANCH in $ALL_BRANCHES; do
  KEEP=false
  for KEEP_BRANCH in "${KEEP_BRANCHES[@]}"; do
    if [[ "$BRANCH" == "$KEEP_BRANCH" ]]; then
      KEEP=true
      break
    fi
  done
  
  if [[ "$KEEP" == "false" ]]; then
    DELETE_BRANCHES+=("$BRANCH")
  fi
done

echo "The following branches will be deleted:"
for BRANCH in "${DELETE_BRANCHES[@]}"; do
  echo "  - $BRANCH"
done
echo ""

# Confirm before proceeding
read -p "Do you want to proceed with deletion? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# Delete local branches
for BRANCH in "${DELETE_BRANCHES[@]}"; do
  echo "Deleting local branch: $BRANCH"
  git branch -D "$BRANCH"
done

# Delete remote branches
for BRANCH in "${DELETE_BRANCHES[@]}"; do
  echo "Deleting remote branch: $BRANCH"
  git push origin --delete "$BRANCH"
done

echo ""
echo "Branch cleanup completed."
