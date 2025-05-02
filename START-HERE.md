# Klaviyo Reporting POC - Getting Started

## Overview

This document provides a step-by-step guide for working with this repository, including how to follow the PR plan, manage branches, and maintain a clean repository.

## Working Through the PR Plan

We are systematically working through the PR list defined in [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md). This plan outlines all the PRs that need to be completed for this project.

### Steps for Working on a PR

1. **Check the PR Plan**: Review [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md) to identify the next PR to work on.

2. **Create a Branch**: Always create branches from the latest `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature-name
   ```

3. **Implement Changes**: Make the necessary changes according to the PR requirements.

4. **Commit and Push**: Regularly commit your changes and push to the remote branch:
   ```bash
   git add .
   git commit -m "Descriptive message about what changed"
   git push origin feature/your-feature-name
   ```

5. **Create a PR**: When your changes are ready, create a PR on GitHub:
   - Title should include the PR number and title from the plan (e.g., "PR 4: Metric Aggregates & Revenue Call")
   - Description should reference the PR plan
   - Follow the validation steps listed in the PR plan

## Merging PRs and Branch Cleanup

### Merging a PR

1. **Review and Approve**: Ensure the PR has been reviewed and approved.

2. **Squash and Merge**: When merging, use the "Squash and merge" option on GitHub:
   - This creates a clean, single commit on the main branch
   - This helps ensure the "Delete branch on merge" option works correctly

3. **Switch Back to Main**: After merging, switch back to the main branch and pull the latest changes:
   ```bash
   git checkout main
   git pull
   ```

### Verifying Branch Deletion

1. **Check Local Branches**: List all local branches to see if the merged branch still exists:
   ```bash
   git branch
   ```

2. **Check Remote Branches**: List all remote branches to see if the merged branch still exists:
   ```bash
   git branch -r
   ```

3. **Clean Up Branches**: If branches are not automatically deleted, run the cleanup script:
   ```bash
   ./scripts/cleanup_branches.sh
   ```

## Branch Cleanup Process

### Automatic Cleanup

The repository has the "Delete branch on merge" setting enabled, which should automatically delete branches after they are merged via a PR.

### Manual Cleanup

If branches are not automatically deleted, you can use the cleanup script:

```bash
./scripts/cleanup_branches.sh
```

This script:
1. Identifies branches that have been merged into main
2. Excludes branches that have open pull requests
3. Deletes both local and remote branches after confirmation

### Troubleshooting Branch Deletion

If branches are not being automatically deleted:

1. Ensure you're using the "Squash and merge" option when merging PRs
2. Check that you're not closing PRs without merging them
3. Run the cleanup script to manually delete merged branches

## Checking PR Status

To see the status of all PRs:

```bash
gh pr list
```

To see details of a specific PR:

```bash
gh pr view <PR-NUMBER>
```

## Next Steps

1. Review the [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md) to identify the next PR to work on
2. Follow the Git workflow guidelines in [docs/git_workflow.md](docs/git_workflow.md)
3. After completing a PR, update the PR plan to mark it as completed

---

For more detailed information about the Git workflow, see [docs/git_workflow.md](docs/git_workflow.md).
