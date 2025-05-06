# Klaviyo Reporting POC - Getting Started

## Current Status

**IMPORTANT: All PRs from the initial phase have been completed as of May 6, 2025.**

We are now moving to the **Narrow Scope POC** implementation phase. The new PR plan is defined in [NARROW_SCOPE_POC_PR_PLAN.md](docs/NARROW_SCOPE_POC_PR_PLAN.md).

## Overview

This document provides a step-by-step guide for working with this repository, including how to follow the PR plan, manage branches, and maintain a clean repository. All team members should start here to understand the workflow.

## Project Roles and Responsibilities

### Developer Role

As a developer, you are responsible for:

1. Implementing the changes required by the PR plan
2. Writing tests for all new functionality and significant changes
3. Creating PRs that follow the project standards
4. Updating the PR plan after your PR is merged

### Reviewer Role

As a reviewer, you are responsible for:

1. Verifying that PRs implement all requirements from the PR plan
2. Checking that validation steps have been completed
3. Ensuring that tests have been written for all new functionality
4. Running the tests to verify they pass
5. Creating tests if the PR lacks adequate test coverage
6. Approving PRs that meet all requirements

### Tester Role

As a tester, you are responsible for:

1. Following the validation steps listed in the PR plan
2. Documenting evidence of successful validation
3. Updating the PR plan with validation evidence

## Working Through the Narrow Scope POC PR Plan

We are now implementing the Narrow Scope POC as defined in [NARROW_SCOPE_POC_PR_PLAN.md](docs/NARROW_SCOPE_POC_PR_PLAN.md). This plan outlines the 6 PRs that need to be completed for this phase of the project.

### Steps for Working on a PR

1. **Check the PR Plan**: Review [NARROW_SCOPE_POC_PR_PLAN.md](docs/NARROW_SCOPE_POC_PR_PLAN.md) to identify the next PR to work on.
   - Look for PRs that don't have checkmarks (`[ ]` instead of `[x]`)
   - Check if there's a specific branch name specified in the PR plan

2. **Create a Branch**: Always create branches from the latest `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature-name
   ```
   - Use the branch name specified in the PR plan when available

3. **Implement Changes**: Make the necessary changes according to the PR requirements.
   - Refer to the PR plan for specific requirements
   - Complete all items listed in the PR description

4. **Commit and Push**: Regularly commit your changes and push to the remote branch:
   ```bash
   git add .
   git commit -m "Descriptive message about what changed"
   git push origin feature/your-feature-name
   ```

5. **Create a PR**: When your changes are ready, create a PR on GitHub:
   - Title: Include the PR number and title from the plan (e.g., "PR 1: Klaviyo API Ingest Script")
   - Description: Reference the PR plan with a link to the document
   - Include a checklist of completed items from the PR plan
   - Document any evidence required by the validation steps

6. **Validation**: Complete all validation steps listed in the PR plan:
   - Run any required tests or commands
   - Document the results as evidence
   - Update the PR description with the evidence

## Merging PRs and Branch Cleanup

### Merging a PR

1. **Review and Approve**: Ensure the PR has been reviewed and approved.
   - All requirements from the PR plan must be implemented
   - All validation steps must be completed successfully

2. **Squash and Merge**: When merging, use the "Squash and merge" option on GitHub:
   - This creates a clean, single commit on the main branch
   - This helps ensure the "Delete branch on merge" option works correctly

3. **Switch Back to Main**: After merging, switch back to the main branch and pull the latest changes:
   ```bash
   git checkout main
   git pull
   ```

4. **Verify Current Branch**: Confirm that you are now on the main branch:
   ```bash
   git branch --show-current
   ```

5. **Update PR Plan**: Update the PR plan to mark the PR as completed:
   - Change the checkbox from `[ ]` to `[x]` for all completed items
   - Add the "Evidence" section with details about the PR merge
   - Commit and push these changes to main

### Verifying Branch Deletion

1. **Check Local Branches**: List all local branches to see if the merged branch still exists:
   ```bash
   git branch
   ```

2. **Check Remote Branches**: List all remote branches to see if the merged branch still exists:
   ```bash
   git fetch --prune
   git branch -r
   ```

3. **Delete Local Branch**: If the local branch still exists, delete it:
   ```bash
   git branch -D feature/your-feature-name
   ```

4. **Clean Up Branches**: If other branches are not automatically deleted, run the cleanup script:
   ```bash
   ./scripts/cleanup_branches.sh
   ```

## Branch Cleanup Process

### Automatic Cleanup

The repository has the "Delete branch on merge" setting enabled, which should automatically delete remote branches after they are merged via a PR.

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

1. Review the [NARROW_SCOPE_POC_PR_PLAN.md](docs/NARROW_SCOPE_POC_PR_PLAN.md) to identify the next PR to work on
2. Follow the detailed Git workflow guidelines in [docs/git_workflow.md](docs/git_workflow.md)
3. After completing a PR, update the PR plan to mark it as completed
4. When all Narrow Scope POC PRs are completed, update this START-HERE.md file to reflect the new status

## Narrow Scope POC Overview

The Narrow Scope POC implementation is divided into 6 sequential PRs:

1. **PR 1: Klaviyo API Ingest Script** - Create a script to fetch campaign metrics from the Klaviyo API
2. **PR 2: LookML Field Mapper** - Normalize Klaviyo fields for Looker Studio
3. **PR 3: Mock Looker Dataset** - Create a mock dataset for testing
4. **PR 4: Test Visualization Stub** - Create a sample Looker Studio JSON config
5. **PR 5: ETL Runner** - Integrate fetch → normalize → export
6. **PR 6: README Updates** - Document the POC pipeline

Detailed implementation guides for each PR are available in the `docs/` directory:

- `docs/PR1_IMPLEMENTATION_GUIDE.md`
- `docs/PR2_IMPLEMENTATION_GUIDE.md`
- `docs/PR3_IMPLEMENTATION_GUIDE.md`
- `docs/PR4_IMPLEMENTATION_GUIDE.md`
- `docs/PR5_IMPLEMENTATION_GUIDE.md`
- `docs/PR6_IMPLEMENTATION_GUIDE.md`

---

For more detailed information about the Git workflow, including role-based instructions and validation processes, see [docs/git_workflow.md](docs/git_workflow.md).
