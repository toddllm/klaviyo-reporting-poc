# GitHub Pull Request Plan

Break the POC plan into focused PRs with validation steps and evidence placeholders.

---

## PR 1: Environment & Config Update
**Branch:** feature/env-config
- [ ] Add `SLACK_WEBHOOK_URL` & `LOOKER_REPORT_URL` to `.env.example` and README.
- [ ] **Also** add defaults in `config.py` so CI tests pass.

**Validation:**
1. Reviewer inspects `.env.example` and `config.py` defaults.
2. Run `python -m pytest tests/test_config.py` (all tests green).

**Merge when these checkboxes are green:**
- [ ] Validation steps passed.

**Evidence:** Paste screenshot or diff URL here.

---

## PR 2: API Edge Cases & Gotchas
**Branch:** feature/api-edge-cases
- [ ] Add **API Edge Cases & Gotchas** section to `POC_plan.md`.
- [ ] Enrich payloads with `relationships.template` and version header.
- [ ] Document `Klaviyo-Api-Version` header in `docs/api_usage.md` and link from README.

**Validation:**
1. `docs/api_usage.md` exists with header docs.
2. README links to `docs/api_usage.md`.

**Merge when these checkboxes are green:**
- [ ] Documentation validated.

**Evidence:** Paste PR diff or screenshot here.

---

## PR 3: Metric Aggregates & Revenue Call
**Branch:** feature/metric-aggregates
- [ ] Implement `get_metric_id(name)` helper in `fetch_metrics.py`.
- [ ] Specify UTC in `start_date`/`end_date` (ISO 8601 UTC).
- [ ] Add `start_date`/`end_date` params and separate revenue fetch.
- [ ] Automate test with `pytest -k test_metric_window`.

**Validation:**
1. `python fetch_metrics.py --dry-run` shows correct UTC window.
2. `pytest -k test_metric_window` passes.

**Merge when these checkboxes are green:**
- [ ] Metric window tests green.

**Evidence:** Attach sample `metrics.csv` & `.metric_ids.json`.

---

## PR 4: Campaign Creation Script
**Branch:** feature/create-send-campaign
- [ ] Create `create_send_campaign.py` combining template assignment and send job.
- [ ] Use correct endpoints, payloads, headers, and add `time.sleep(10)` or poll for `message.status == 'ready'` after template assign.

**Validation:**
1. Run with `--dry-run`, observe logged API requests.
2. Fetch `GET /api/campaigns/<id>` and assert `status=='ready'` before send job.

**Merge when these checkboxes are green:**
- [ ] Propagation check passed.

**Evidence:** Insert console log snippet or link.

---

## PR 5: Profile Seeding & Flags
**Branch:** feature/seed-profiles
- [ ] Ensure `seed_profiles.py` treats HTTP 201 and 202 as OK (idempotent).
- [ ] Add `--prefix foo@yourtest.tld` flag for deterministic addresses in CI.

**Validation:**
1. `python seed_profiles.py --dry-run` prints planned actions.
2. Running real mode creates N profiles; rerun with same prefix returns HTTP 202 treated as success.

**Merge when these checkboxes are green:**
- [ ] Idempotency validated.

**Evidence:** CLI output or API call log.

---

## PR 6: Simulate Events Script
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

## PR 7: Dashboarding & Sheets Integration
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

## PR 8: AI Insights Enhancements
**Branch:** feature/ai-insights
- [ ] Enhance `ai_insights.py` prompt per spec.
- [ ] Include `<meta charset="utf-8">` in `summary.html` header.
- [ ] Add unit test `pytest -k test_ai_summary` to assert output contains 'Open rate'.

**Validation:**
1. Run on sample `metrics.csv`, confirm `summary.html` and test passes.

**Merge when these checkboxes are green:**
- [ ] AI summary tests passed.

**Evidence:** Paste generated summary and HTML snippet.

---

## PR 9: Orchestration & Polling
**Branch:** feature/orchestration
- [ ] Create `run_poc.sh` with `set -euo pipefail` at top and polling guard.

**Validation:**
1. Execute `bash run_poc.sh --dry-run` under `MODE=mock`, ensure exit code 0.
2. Polling logic triggers correctly when metrics not ready.

**Merge when these checkboxes are green:**
- [ ] Orchestration script validated.

**Evidence:** Console transcript.

---

## PR 10: Documentation & Release
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

⚠️ **Re-order note:** Merge PR 4 (Campaign Creation) **before** PR 3 (Metric Aggregates).

> After each PR merge, assign a tester to follow the **Validation** steps and attach **Evidence**. Once all PRs are merged and validated, the POC is ready for Clara’s live demo. 🚀
