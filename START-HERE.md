# Klaviyo Reporting POC - Getting Started

## Current Status

**IMPORTANT: All PRs from the initial phase have been completed as of May 6, 2025.**

**UPDATE: All PRs for the Narrow Scope POC implementation phase have been completed as of May 6, 2025.**

**NEW: The project has shifted from Supermetrics to Fivetran + BigQuery integration. PRs 13-20 have been identified for implementing this new approach.**

**LATEST: A new batch of PRs has been defined for implementing BigQuery sanity checks. See [BQ_SANITY_PR_PLAN.md](docs/BQ_SANITY_PR_PLAN.md) for details.**

**NEW DEMO-READY PLAN: A client-facing demo plan has been created with PRs 22-26 to build a complete reporting solution. See [DEMO_READY_PR_PLAN.md](docs/DEMO_READY_PR_PLAN.md) for details.**

The Narrow Scope POC has been successfully implemented according to the initial PR plan. All 6 initial PRs have been merged and the implementation is now ready for demonstration. The project is now moving to a Fivetran + BigQuery integration approach as defined in [FIVETRAN_BIGQUERY_PR_PLAN.md](docs/FIVETRAN_BIGQUERY_PR_PLAN.md), which replaces the previously planned Supermetrics integration.

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

## Working Through the PR Plans

### Fivetran + BigQuery Integration PR Plan

We are currently implementing the Fivetran + BigQuery integration as defined in [FIVETRAN_BIGQUERY_PR_PLAN.md](docs/FIVETRAN_BIGQUERY_PR_PLAN.md). This plan outlines the PRs (13-20) that need to be completed for this phase of the project.

### BigQuery Sanity Check PR Plan

After completing the Fivetran + BigQuery integration, we will implement the BigQuery sanity checks as defined in [BQ_SANITY_PR_PLAN.md](docs/BQ_SANITY_PR_PLAN.md). This plan introduces an automated BigQuery sanity-check step that can run locally, as part of the end-to-end demo, and in CI.

### Demo-Ready PR Plan

To prepare for client-facing demonstrations, we have defined a new set of PRs (22-26) in [DEMO_READY_PR_PLAN.md](docs/DEMO_READY_PR_PLAN.md). This plan focuses on creating a complete reporting solution with BigQuery views, Looker Studio dashboards, and optional Google Sheets exports that can be used to demonstrate the value of our solution to clients.

### Steps for Working on a PR

1. **Check the PR Plan**: Review the appropriate PR plan document to identify the next PR to work on.
   - For Fivetran + BigQuery integration: [FIVETRAN_BIGQUERY_PR_PLAN.md](docs/FIVETRAN_BIGQUERY_PR_PLAN.md)
   - For BigQuery sanity checks: [BQ_SANITY_PR_PLAN.md](docs/BQ_SANITY_PR_PLAN.md)
   - For client-facing demo preparation: [DEMO_READY_PR_PLAN.md](docs/DEMO_READY_PR_PLAN.md)
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

1. All initial PRs (1-6) in the original Narrow Scope POC PR Plan have been completed
2. The Narrow Scope POC is now ready for demonstration and evaluation
3. Implement the Fivetran + BigQuery integration PRs (13-20) as defined in [FIVETRAN_BIGQUERY_PR_PLAN.md](docs/FIVETRAN_BIGQUERY_PR_PLAN.md):
   - PR 13: Fivetran API Client
   - PR 14: Connector Runner (Trigger + Wait)
   - PR 15: Postgres Extract → CSV Export
   - PR 16: ETL Runner v2 (`--source fivetran`)
   - PR 17: S3 Uploader Utility
   - PR 18: Live ETL Runner (Fivetran → CSV → S3)
   - PR 19: AWS SES Email Smoke Test
   - PR 20: Documentation & .env Template
4. Implement the BigQuery Sanity Check PRs as defined in [BQ_SANITY_PR_PLAN.md](docs/BQ_SANITY_PR_PLAN.md):
   - PR: BigQuery Sanity-Check Script (Python)
   - PR: Hook Sanity Check into End-to-End Demo
   - PR: CI Job: Nightly Sanity Check
   - PR: Docs & Env Template Update
5. Implement the Demo-Ready PRs (22-26) as defined in [DEMO_READY_PR_PLAN.md](docs/DEMO_READY_PR_PLAN.md):
   - PR 22: BigQuery Reporting View + Permissions
   - PR 23: Looker Studio Template JSON
   - PR 24: Google Sheets Exporter (Optional Upsell)
   - PR 25: Demo Orchestrator v2
   - PR 26: Client Demo Docs & Slide Deck
6. For future development, continue to follow the detailed Git workflow guidelines in [docs/git_workflow.md](docs/git_workflow.md)
7. Any new features or enhancements should be discussed with the team before creating new branches or PRs

## Project Overview

The project implementation is divided into four phases:

### Phase 1: Core Implementation (Completed)

1. **PR 1: Klaviyo API Ingest Script** - Create a script to fetch campaign metrics from the Klaviyo API
2. **PR 2: LookML Field Mapper** - Normalize Klaviyo fields for Looker Studio
3. **PR 3: Mock Looker Dataset** - Create a mock dataset for testing
4. **PR 4: Test Visualization Stub** - Create a sample Looker Studio JSON config
5. **PR 5: ETL Runner** - Integrate fetch → normalize → export
6. **PR 6: README Updates** - Document the POC pipeline

### Phase 2: Fivetran + BigQuery Integration (Current Focus)

13. **PR 13: Fivetran API Client** - Create a client for interacting with the Fivetran API
14. **PR 14: Connector Runner** - Trigger Fivetran syncs and wait for completion
15. **PR 15: Postgres Extract → CSV Export** - Extract data from Fivetran's Postgres destination
16. **PR 16: ETL Runner v2** - Extend ETL runner to support Fivetran as a source
17. **PR 17: S3 Uploader Utility** - Upload processed data to S3 for archiving
18. **PR 18: Live ETL Runner** - Implement end-to-end pipeline from Fivetran to S3
19. **PR 19: AWS SES Email Smoke Test** - Send test emails via AWS SES
20. **PR 20: Documentation & .env Template** - Update documentation for the new integration

### Phase 3: BigQuery Sanity Checks (Upcoming)

- **BigQuery Sanity-Check Script** - Python script to verify BigQuery tables
- **End-to-End Demo Integration** - Add sanity checks to the end-to-end demo
- **CI Job: Nightly Sanity Check** - Automated nightly verification
- **Documentation & Environment Updates** - Update docs and environment templates

### Phase 4: Demo-Ready Implementation (Planned)

22. **PR 22: BigQuery Reporting View + Permissions** - Create a reporting view in BigQuery for client-facing metrics
23. **PR 23: Looker Studio Template JSON** - Create a Looker Studio dashboard template for client demos
24. **PR 24: Google Sheets Exporter** - Create a utility to export metrics to Google Sheets as an upsell option
25. **PR 25: Demo Orchestrator v2** - Extend the end-to-end demo script to include all components
26. **PR 26: Client Demo Docs & Slide Deck** - Create documentation and presentation materials for client demos

Detailed implementation guides for Phase 1 PRs are available in the `docs/` directory:

- `docs/PR1_IMPLEMENTATION_GUIDE.md`
- `docs/PR2_IMPLEMENTATION_GUIDE.md`
- `docs/PR3_IMPLEMENTATION_GUIDE.md`
- `docs/PR4_IMPLEMENTATION_GUIDE.md`
- `docs/PR5_IMPLEMENTATION_GUIDE.md`
- `docs/PR6_IMPLEMENTATION_GUIDE.md`

Implementation details for Phase 2 can be found in [FIVETRAN_BIGQUERY_PR_PLAN.md](docs/FIVETRAN_BIGQUERY_PR_PLAN.md), details for Phase 3 can be found in [BQ_SANITY_PR_PLAN.md](docs/BQ_SANITY_PR_PLAN.md), and details for Phase 4 can be found in [DEMO_READY_PR_PLAN.md](docs/DEMO_READY_PR_PLAN.md).

---

For more detailed information about the Git workflow, including role-based instructions and validation processes, see [docs/git_workflow.md](docs/git_workflow.md).
