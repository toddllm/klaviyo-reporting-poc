# GitHub Pull Request Plan

⚠️ **IMPORTANT: ALL DEVELOPERS MUST FOLLOW THIS PLAN** ⚠️

This document outlines the specific PRs that should be created for this project. 

**REQUIRED ACTIONS FOR ALL DEVELOPERS:**

1. **REFERENCE THIS PLAN IN EVERY PR DESCRIPTION** with a link to this document
2. **INCLUDE THE PR NUMBER AND TITLE FROM THIS PLAN** in your PR title
3. **ENSURE YOUR PR ALIGNS WITH ONE OF THE ITEMS BELOW**

**DO NOT create PRs that are not part of this plan without discussing with the team first.**

**EXAMPLE PR TITLE:** "PR 3: API Edge Cases & Gotchas"

**EXAMPLE PR DESCRIPTION START:**
```
Implements PR #3 from the [GitHub PR Plan](../docs/GITHUB_PR_PLAN.md).

This PR adds API edge case documentation and implements version header handling.
```

---

## PR 1: Environment & Config Update ✅
**Branch:** feature/github-pr-plan-review-20250502-113408
- [x] Add `SLACK_WEBHOOK_URL` & `LOOKER_REPORT_URL` to `.env.example` and README.
- [x] **Also** add defaults in `config.py` so CI tests pass.

**Validation:**
1. Reviewer inspects `.env.example` and `config.py` defaults.
2. Run `python -m pytest tests/test_config.py` (all tests green).

**Merge when these checkboxes are green:**
- [x] Validation steps passed.

**Evidence:** PR #1 merged on May 2, 2025.

---

## PR 2: Slack Integration Implementation ✅
**Branch:** feature/slack-integration-20250502
- [x] Create `slack_integration.py` for sending reports to Slack
- [x] Add tests for Slack integration functionality
- [x] Update README with Slack integration documentation

**Validation:**
1. Run `python -m pytest tests/test_slack_integration.py` (all tests green).
2. Verify Slack message formatting in mock mode.

**Merge when these checkboxes are green:**
- [x] Slack integration tests passed.

**Evidence:** PR #2 merged on May 2, 2025.

---

## PR 3: API Edge Cases & Gotchas ✅
**Branch:** feature/api-edge-cases
- [x] Add **API Edge Cases & Gotchas** section to `POC_plan.md`.
- [x] Enrich payloads with `relationships.template` and version header.
- [x] Document `Klaviyo-Api-Version` header in `docs/api_usage.md` and link from README.

**Validation:**
1. `docs/api_usage.md` exists with header docs.
2. README links to `docs/api_usage.md`.

**Merge when these checkboxes are green:**
- [x] Documentation validated.

**Evidence:** PR #4 merged on May 2, 2025. Added API usage guidelines document with version header documentation and updated POC_plan.md with additional API edge cases.

---

## PR 4: Metric Aggregates & Revenue Call ✅
**Branch:** feature/metric-aggregates
- [x] Implement `get_metric_id(name)` helper in `fetch_metrics.py`.
- [x] Specify UTC in `start_date`/`end_date` (ISO 8601 UTC).
- [x] Add `start_date`/`end_date` params and separate revenue fetch.
- [x] Automate test with `pytest -k test_metric_window`.

**Validation:**
1. `python fetch_metrics.py --dry-run` shows correct UTC window.
2. `pytest -k test_metric_window` passes.

**Merge when these checkboxes are green:**
- [x] Metric window tests green.

**Evidence:** PR #14 merged on May 2, 2025. Updated datetime handling to use timezone-aware objects and implemented proper metric ID caching with `.metric_ids.json`. All tests pass successfully.

---

## PR 5: Campaign Creation Script ✅
**Branch:** feature/create-send-campaign
- [x] Create `create_send_campaign.py` combining template assignment and send job.
- [x] Use correct endpoints, payloads, headers, and add `time.sleep(10)` or poll for `message.status == 'ready'` after template assign.

**Validation:**
1. Run with `--dry-run`, observe logged API requests.
2. Fetch `GET /api/campaigns/<id>` and assert `status=='ready'` before send job.

**Merge when these checkboxes are green:**
- [x] Propagation check passed.

**Evidence:** PR #5 merged on May 2, 2025. Added create_send_campaign.py with proper template assignment and polling for message.status, along with comprehensive unit tests.

---

## PR 6: Profile Seeding & Flags ✅
**Branch:** feature/read-start-here-md-and-create-next-pr-20250502-161039
- [x] Ensure `seed_profiles.py` treats HTTP 201 and 202 as OK (idempotent).
- [x] Add `--prefix foo@yourtest.tld` flag for deterministic addresses in CI.

**Validation:**
1. `python seed_profiles.py --dry-run` prints planned actions.
2. Running real mode creates N profiles; rerun with same prefix returns HTTP 202 treated as success.

**Merge when these checkboxes are green:**
- [x] Idempotency validated.

**Evidence:** PR #18 merged on May 2, 2025. Added proper handling of HTTP 201 and 202 status codes for idempotent operations and improved --prefix flag documentation for deterministic email addresses in CI environments. All tests pass successfully.

---

## PR 7: Simulate Events Script
**Branch:** feature/simulate-events
- [ ] Rename `simulate_open.py` → `simulate_events.py`.
- [ ] Ensure payload includes `metric_id` inside `metric` object per API v2025-04-15.
- [ ] Provide helper `get_or_create_custom_metric(name)`.

**Validation:**
1. `python simulate_events.py --dry-run` shows payloads with correct `metric_id` field.

**Merge when these checkboxes are green:**
- [ ] Payload structure validated.

**Evidence:** Dry-run log snippet.

---

## PR 8: Dashboarding & Sheets Integration
**Branch:** feature/dashboard
- [ ] Update `push_to_sheet.py` to use `worksheet.update(data, value_input_option='RAW')`.
- [ ] Script named-range via `gspread.utils.set_named_range()`.

**Validation:**
1. Run `python push_to_sheet.py`, confirm sheet updated within named range without quota errors.
2. Link to Looker dashboard showing recent refresh timestamp.

**Evidence:** Paste dashboard link.

**Merge when these checkboxes are green:**
- [ ] Dashboard refresh validated.

---

## PR 9: AI Insights Enhancements
**Branch:** feature/ai-insights-20250502
- [ ] Enhance `ai_insights.py` prompt per spec.
- [ ] Include `<meta charset="utf-8">` in `summary.html` header.
- [ ] Add unit test `pytest -k test_ai_summary` to assert output contains 'Open rate'.

**Validation:**
1. Run on sample `metrics.csv`, confirm `summary.html` and test passes.

**Merge when these checkboxes are green:**
- [ ] AI summary tests passed.

**Evidence:** Paste generated summary and HTML snippet.

---

## PR 10: Orchestration & Polling
**Branch:** feature/orchestration
- [ ] Create `run_poc.sh` with `set -euo pipefail` at top and polling guard.

**Validation:**
1. Execute `bash run_poc.sh --dry-run` under `MODE=mock`, ensure exit code 0.
2. Polling logic triggers correctly when metrics not ready.

**Merge when these checkboxes are green:**
- [ ] Orchestration script validated.

**Evidence:** Console transcript.

---

## PR 11: Documentation & Release
**Branch:** feature/documentation
- [ ] Move call-flow diagram to `docs/img/flow.svg` and reference it in README.
- [ ] Lint README with `markdownlint`.

**Validation:**
1. `docs/img/flow.svg` exists and README displays it.
2. `markdownlint README.md` returns no errors.

**Merge when these checkboxes are green:**
- [ ] Documentation lint passed.

**Evidence:** Preview link or screenshot of README.

---

⚠️ **Re-order note:** Merge PR 5 (Campaign Creation) **before** PR 4 (Metric Aggregates).

> After each PR merge, assign a tester to follow the **Validation** steps and attach **Evidence**. Once all PRs are merged and validated, the POC is ready for Clara’s live demo. 🚀
