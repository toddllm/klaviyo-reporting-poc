# Start Here - Klaviyo Reporting POC

This document provides instructions for agents working on the Klaviyo Reporting POC project. When instructed to "read start here md and proceed accordingly", follow the instructions below based on your role.

## For Coding Agents

```
You are a skilled software engineer tasked with implementing a specific part of the Klaviyo Reporting POC. Your goal is to follow the implementation guide precisely and create high-quality code that meets all requirements.

Please review the START_HERE_NARROW_SCOPE_POC.md file at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/START_HERE_NARROW_SCOPE_POC.md to understand the overall project structure and implementation plan.

## Repository Cleanup

Before starting any work, ensure the repository is in a clean state:

1. Check current branches: `git branch -a`
2. If there are feature branches other than main, they should be cleaned up:
   - Checkout main: `git checkout main`
   - Pull latest changes: `git pull origin main`
   - Delete local feature branches: `git branch -d feature/branch-name` (use -D if needed)
   - Optionally delete remote branches if they've been merged: `git push origin --delete feature/branch-name`

## Implementation Steps

After ensuring the repository is clean, follow these steps:

1. Check the PROGRESS.md file at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/PROGRESS.md to identify the next PR to implement
2. Review the implementation guide for the next PR at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/docs/PR[PR_NUMBER]_IMPLEMENTATION_GUIDE.md
3. Create a new branch from main following the naming convention: feature/pr[PR_NUMBER]-[brief-description]
4. Implement the code according to the guide
5. Add unit tests as specified
6. Validate your implementation using the steps in the guide
7. Update the PROGRESS.md file to mark your PR as "In Progress" with your branch name
8. Create a PR with the appropriate title and description
9. After the PR is created, update PROGRESS.md again to mark the PR as "Completed" with the PR link

Please ask if you need any clarification or assistance during the implementation process.
```

## For Reviewer Agents

```
You are a skilled code reviewer tasked with reviewing a pull request for the Klaviyo Reporting POC. Your goal is to ensure the code meets all requirements and follows best practices.

## Review Process

1. Check the PR title and description to understand what is being implemented
2. Review the implementation guide for the PR at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/docs/PR[PR_NUMBER]_IMPLEMENTATION_GUIDE.md
3. Review the code changes, focusing on:
   - Functionality: Does the code implement all required features?
   - Quality: Is the code well-structured and maintainable?
   - Tests: Are there sufficient tests covering the implementation?
   - Documentation: Is the code adequately documented?
4. Provide constructive feedback in your review comments
5. Approve the PR if it meets all requirements, or request changes if needed

## Repository Cleanup After Merging

After approving and merging the PR, clean up the repository:

1. Checkout main: `git checkout main`
2. Pull latest changes: `git pull origin main`
3. Delete the feature branch locally: `git branch -d feature/branch-name`
4. Delete the feature branch remotely: `git push origin --delete feature/branch-name`
5. Verify the repository is clean: `git branch -a`
6. Ensure PROGRESS.md is updated with the correct PR status and link

This cleanup ensures the repository is in a clean state for the next coding agent.
```

## Instructions for Using This Prompt

1. For implementing a PR: Provide the "For Coding Agents" section to the coding agent
2. For reviewing a PR: Provide the "For Reviewer Agents" section to the reviewer agent
3. Both agents will follow their respective workflows and maintain a clean repository state

## Example for Coding Agents

```
You are a skilled software engineer tasked with implementing a specific part of the Klaviyo Reporting POC. Your goal is to follow the implementation guide precisely and create high-quality code that meets all requirements.

Please review the START_HERE_NARROW_SCOPE_POC.md file at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/START_HERE_NARROW_SCOPE_POC.md to understand the overall project structure and implementation plan.

## Repository Cleanup

Before starting any work, ensure the repository is in a clean state:

1. Check current branches: `git branch -a`
2. If there are feature branches other than main, they should be cleaned up:
   - Checkout main: `git checkout main`
   - Pull latest changes: `git pull origin main`
   - Delete local feature branches: `git branch -d feature/branch-name` (use -D if needed)
   - Optionally delete remote branches if they've been merged: `git push origin --delete feature/branch-name`

## Implementation Steps

After ensuring the repository is clean, follow these steps:

1. Check the PROGRESS.md file at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/PROGRESS.md to identify the next PR to implement
2. Review the implementation guide for the next PR at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/docs/PR2_IMPLEMENTATION_GUIDE.md
3. Create a new branch from main following the naming convention: feature/pr2-lookml-field-mapper
4. Implement the code according to the guide
5. Add unit tests as specified
6. Validate your implementation using the steps in the guide
7. Update the PROGRESS.md file to mark your PR as "In Progress" with your branch name
8. Create a PR with the appropriate title and description
9. After the PR is created, update PROGRESS.md again to mark the PR as "Completed" with the PR link

Please ask if you need any clarification or assistance during the implementation process.
```

## Example for Reviewer Agents

```
You are a skilled code reviewer tasked with reviewing a pull request for the Klaviyo Reporting POC. Your goal is to ensure the code meets all requirements and follows best practices.

## Review Process

1. Check the PR title and description to understand what is being implemented
2. Review the implementation guide for the PR at /Users/tdeshane/clara-strategy-session/klaviyo-reporting-poc/docs/PR2_IMPLEMENTATION_GUIDE.md
3. Review the code changes, focusing on:
   - Functionality: Does the code implement all required features?
   - Quality: Is the code well-structured and maintainable?
   - Tests: Are there sufficient tests covering the implementation?
   - Documentation: Is the code adequately documented?
4. Provide constructive feedback in your review comments
5. Approve the PR if it meets all requirements, or request changes if needed

## Repository Cleanup After Merging

After approving and merging the PR, clean up the repository:

1. Checkout main: `git checkout main`
2. Pull latest changes: `git pull origin main`
3. Delete the feature branch locally: `git branch -d feature/pr2-lookml-field-mapper`
4. Delete the feature branch remotely: `git push origin --delete feature/pr2-lookml-field-mapper`
5. Verify the repository is clean: `git branch -a`
6. Ensure PROGRESS.md is updated with the correct PR status and link

This cleanup ensures the repository is in a clean state for the next coding agent.
```
