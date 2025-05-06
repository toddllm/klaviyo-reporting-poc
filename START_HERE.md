# Klaviyo Reporting POC - Start Here

## When instructed to "read start here md and proceed accordingly"

When you receive the instruction "read start here md and proceed accordingly", you should:

1. Review this document to understand the project structure and workflow
2. Check the PR plan in [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md) to identify the next PR to implement
3. Follow the implementation guide for that PR in the docs directory
4. Create a new branch from main with the appropriate naming convention
5. Implement the required changes and tests
6. Create a PR with the appropriate title and description

## Project Overview

This repository contains a Proof of Concept (POC) for Klaviyo reporting integration. The project is structured as a series of PRs that build upon each other to create a complete reporting solution.

## Working Through the PR Plan

We are systematically working through the PR list defined in [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md). This plan outlines all the PRs that need to be completed for this project.

### Steps for Working on a PR

1. **Check the PR Plan**: Review [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md) to identify the next PR to work on.
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
   - Title: Include the PR number and title from the plan (e.g., "PR 4: Metric Aggregates & Revenue Call")
   - Description: Reference the PR plan with a link to the document
   - Include a checklist of completed items from the PR plan
   - Document any evidence required by the validation steps

6. **Validation**: Complete all validation steps listed in the PR plan:
   - Run any required tests or commands
   - Document the results as evidence
   - Update the PR description with the evidence

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

### Branch Cleanup Process

After merging a PR, it's important to clean up branches to keep the repository organized:

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

4. **Delete Remote Branch**: If the remote branch still exists, delete it:
   ```bash
   git push origin --delete feature/your-feature-name
   ```

## Next Steps

1. Review the [GITHUB_PR_PLAN.md](docs/GITHUB_PR_PLAN.md) to identify the next PR to work on
2. Follow the detailed implementation guide for that PR in the docs directory
3. Create a new branch from main with the appropriate naming convention
4. Implement the required changes and tests
5. Create a PR with the appropriate title and description

---

For more detailed information about the Git workflow, including role-based instructions and validation processes, see [docs/git_workflow.md](docs/git_workflow.md).
