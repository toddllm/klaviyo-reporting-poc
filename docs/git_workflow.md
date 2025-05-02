# Git Workflow Guidelines

## Branch Management

### Creating a Branch

1. Always create branches from the latest `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature-name
   ```

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

2. Create a Pull Request on GitHub with a clear title and description.

### Merging a Pull Request

1. **Important**: When merging a PR on GitHub, use the "Squash and merge" option.
   - This creates a clean, single commit on the main branch
   - This ensures the "Delete branch on merge" option works correctly

2. After merging, the branch should be automatically deleted on GitHub.

### Cleaning Up Branches

Periodically run the cleanup script to remove merged branches:

```bash
./scripts/cleanup_branches.sh
```

## Repository Settings

The repository has the following settings enabled:

- **Delete branch on merge**: Automatically deletes the branch after a PR is merged
- **Squash merging**: Combines all commits into a single commit when merging

## Troubleshooting

If branches are not being automatically deleted after merging:

1. Ensure you're using the "Squash and merge" option when merging PRs
2. Check that the "Delete branch on merge" option is enabled in the repository settings
3. Run the cleanup script to manually delete merged branches
