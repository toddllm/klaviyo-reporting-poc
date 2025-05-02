#!/bin/bash

# Efficient script to clean up merged branches without requiring user input
# Created as part of the branch cleanup task

# Get the current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# List of branches to keep (add any WIP branches here)
KEEP_BRANCHES=(
  "$CURRENT_BRANCH"
  "main"
  "feature/verify-start-here-md-and-resolve-issues-20250502-170718" # Not in PR list, might be WIP
)

# List of branches we know are merged based on PR history
MERGED_BRANCHES=(
  "feature/ai-insights-20250502"
  "feature/cleanup-merged-branches-and-open-prs-20250502-163521"
  "feature/read-start-here-md-and-create-next-pr-20250502-161039"
  "fix/pr-labeling"
)

echo "\nBranches identified as merged from PR history:"
for BRANCH in "${MERGED_BRANCHES[@]}"; do
  echo "  - $BRANCH"
done

# Filter out branches we want to keep
BRANCHES_TO_DELETE=()
for BRANCH in "${MERGED_BRANCHES[@]}"; do
  KEEP=false
  for KEEP_BRANCH in "${KEEP_BRANCHES[@]}"; do
    if [[ "$BRANCH" == "$KEEP_BRANCH" ]]; then
      KEEP=true
      break
    fi
  done
  
  if [[ "$KEEP" == "false" ]]; then
    BRANCHES_TO_DELETE+=("$BRANCH")
  fi
done

echo "\nBranches that will be deleted:"
for BRANCH in "${BRANCHES_TO_DELETE[@]}"; do
  echo "  - $BRANCH"
done

# Delete local branches
for BRANCH in "${BRANCHES_TO_DELETE[@]}"; do
  echo "\nDeleting local branch: $BRANCH"
  git branch -D "$BRANCH" || echo "Failed to delete local branch: $BRANCH"
done

# Check if remote branches exist before trying to delete them
echo "\nChecking for remote branches..."
git fetch --prune
REMOTE_BRANCHES=$(git branch -r | sed 's/origin\///')

# Delete remote branches if they exist
for BRANCH in "${BRANCHES_TO_DELETE[@]}"; do
  if echo "$REMOTE_BRANCHES" | grep -q "$BRANCH"; then
    echo "Deleting remote branch: $BRANCH"
    git push origin --delete "$BRANCH" || echo "Failed to delete remote branch: $BRANCH"
  else
    echo "Remote branch does not exist: $BRANCH"
  fi
done

echo "\nBranch cleanup completed."

# Document the cleanup in a markdown file
DOC_FILE="CLEANUP_REPORT.md"
echo "# Branch Cleanup Report" > "$DOC_FILE"
echo "" >> "$DOC_FILE"
echo "Date: $(date)" >> "$DOC_FILE"
echo "" >> "$DOC_FILE"
echo "## Branches Kept" >> "$DOC_FILE"
for BRANCH in "${KEEP_BRANCHES[@]}"; do
  echo "- $BRANCH" >> "$DOC_FILE"
done
echo "" >> "$DOC_FILE"
echo "## Branches Deleted" >> "$DOC_FILE"
for BRANCH in "${BRANCHES_TO_DELETE[@]}"; do
  echo "- $BRANCH" >> "$DOC_FILE"
done
echo "" >> "$DOC_FILE"
echo "## Summary" >> "$DOC_FILE"
echo "Total branches kept: ${#KEEP_BRANCHES[@]}" >> "$DOC_FILE"
echo "Total branches deleted: ${#BRANCHES_TO_DELETE[@]}" >> "$DOC_FILE"
echo "" >> "$DOC_FILE"

echo "Cleanup report saved to $DOC_FILE"
