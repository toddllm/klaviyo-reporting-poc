# Git Workflow Guidelines

## Role-Based Workflow

### Developer Role

1. Check the [GITHUB_PR_PLAN.md](GITHUB_PR_PLAN.md) to identify the next PR to work on
2. Create a branch and implement the required changes
3. Write tests for all new functionality and significant changes
4. Run tests to ensure they pass before creating a PR
5. Create a PR with proper references to the PR plan
6. Address review comments
7. After PR is merged, update the PR plan to mark the PR as completed

### Reviewer Role

1. Review the PR against the requirements in the PR plan
2. Verify that all validation steps listed in the PR plan are completed
3. Ensure that tests have been written for all new functionality
4. Run the tests to verify they pass
5. Create tests if the PR lacks adequate test coverage
6. Approve the PR if all requirements are met

### Tester Role

1. Follow the validation steps listed in the PR plan
2. Document evidence of successful validation
3. Update the PR plan with the evidence

## Branch Management

### Creating a Branch

1. Always create branches from the latest `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Use the branch naming convention specified in the PR plan when available

### Working on a Branch

1. Commit your changes frequently with meaningful commit messages:
   ```bash
   git add .
   git commit -m "Descriptive message about what changed"
   ```

2. Push your branch to remote to save your work:
   ```bash
   git push -u origin feature/your-feature-name
   ```

### Creating a Pull Request

1. Push your final changes to the remote branch:
   ```bash
   git add .
   git commit -m "Final changes for PR"
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request on GitHub with:
   - Title: Include the PR number and title from the PR plan (e.g., "PR 4: Metric Aggregates & Revenue Call")
   - Description: Reference the PR plan and describe what was implemented
   - Include any evidence required by the validation steps

### PR Review Process

1. Reviewers should check that the PR implements all requirements listed in the PR plan
2. Verify that all validation steps have been completed successfully
3. Check that the code follows project standards
4. Ensure that tests have been written for all new functionality
5. Run the tests to verify they pass
6. Create tests if the PR lacks adequate test coverage
7. Approve the PR when all requirements are met

### Merging a Pull Request

1. **Important**: When merging a PR on GitHub, use the "Squash and merge" option.
   - This creates a clean, single commit on the main branch
   - This ensures the "Delete branch on merge" option works correctly

2. After merging, the branch should be automatically deleted on GitHub.

3. Switch back to the main branch and pull the latest changes:
   ```bash
   git checkout main
   git pull
   ```

4. Verify that you are now on the main branch:
   ```bash
   git branch --show-current
   ```

5. Update the PR plan to mark the PR as completed:
   - Change the checkbox from `[ ]` to `[x]` for all completed items
   - Add the "Evidence" section with details about the PR merge
   - Commit and push these changes to main

6. **IMPORTANT**: Clean up branches immediately after every merge:
   ```bash
   ./scripts/cleanup_branches.sh
   ```
   - This keeps the repository clean and prevents confusion
   - Do not wait to clean up branches - do it immediately after each merge
   - This is a critical step that should never be skipped

### Cleaning Up Branches

1. After merging a PR, verify that the remote branch was deleted:
   ```bash
   git fetch --prune
   git branch -r
   ```

2. Delete the local branch if it still exists:
   ```bash
   git branch -D feature/your-feature-name
   ```

3. Periodically run the cleanup script to remove any remaining merged branches:
   ```bash
   ./scripts/cleanup_branches.sh
   ```

The cleanup script:
1. Identifies branches that have been merged into main
2. Excludes branches that have open pull requests
3. Deletes both local and remote branches after confirmation

## Validation Process

1. Each PR in the PR plan has specific validation steps
2. Complete all validation steps before merging the PR
3. Document evidence of successful validation as specified in the PR plan
4. Update the PR plan with the evidence after merging

## Repository Settings

The repository has the following settings enabled:

- **Delete branch on merge**: Automatically deletes the branch after a PR is merged
- **Squash merging**: Combines all commits into a single commit when merging

## Troubleshooting

If branches are not being automatically deleted after merging:

1. Ensure you're using the "Squash and merge" option when merging PRs
2. Check that the "Delete branch on merge" option is enabled in the repository settings
3. Run the cleanup script to manually delete merged branches

Common issues:
- If PRs are closed without merging, branches won't be automatically deleted
- If PRs are merged using methods other than "Squash and merge", the automatic deletion might not work correctly
- The GitHub API sometimes has delays in processing branch deletions
