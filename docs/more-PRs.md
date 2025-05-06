# Additional PRs for Narrow Scope POC  
*(supplements the existing "Narrow Scope POC PR Plan" – begin numbering at 7 to avoid collisions)*  

⚠️ **REMINDER:** Every PR **must** reference this plan in its description and follow the stated validation checklist.  

---

## PR 7: Supermetrics → CSV Pull Script  
**Branch:** `feature/supermetrics-klaviyo-pull`  
- [x] Add `src/supermetrics_klaviyo_pull.py` – CLI script that pulls Klaviyo data via Supermetrics API (JSON‐based connector end‑point)  
- [x] Support auth via `SUPERMETRICS_API_KEY` env var  
- [x] Accept params: `--start-date`, `--end-date`, `--report-type` (campaign | events)  
- [x] Write results to `data/supermetrics_raw_YYYYMMDD.json` and optional CSV  
- [x] Retry & rate‑limit logic per Supermetrics guidelines  
- [x] Unit tests: `tests/test_supermetrics_klaviyo_pull.py` (mock HTTP responses)  

**Validation**  
1. Dev ► Run dry‑run: `python src/supermetrics_klaviyo_pull.py --start-date 2025-05-01 --end-date 2025-05-02 --report-type campaign --dry-run`  
2. Dev ► Run full fetch; confirm JSON/CSV written with ≥1 row  
3. Reviewer ► Verify pagination + rate‑limit handling works with mocked 429 response  
4. Reviewer ► Confirm output schema matches mapper expectations  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #45 created on May 6, 2025
- All tests passing: `pytest tests/test_supermetrics_klaviyo_pull.py`
- Implementation includes API key authentication, pagination, error handling, and CSV/JSON output
- Dry run functionality works as expected

---

## PR 8: BigQuery Loader (Optional Warehouse Path)  
**Branch:** `feature/bq-loader`  
- [x] Add `src/bq_loader.py` to load Supermetrics‑generated CSV/JSON into BigQuery table `klaviyo_raw.events`  
- [x] Use `google-cloud-bigquery` client; creds via service‑account JSON  
- [x] Schema auto‑detect + partition by `date` column  
- [x] Add CI step `pytest tests/test_bq_loader.py` with BigQuery emulator (or mock)  

**Validation**  
1. Dev ► Load sample file from PR 7 into a local/emulated BQ instance  
2. Dev ► Query table; ensure row count matches source file  
3. Reviewer ► Confirm partitioning & clustering flags set  
4. Reviewer ► Check idempotency (re‑running loader does not duplicate rows)  

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #46 merged on May 6, 2025
- All tests passing: `pytest tests/test_bq_loader.py`
- Implementation includes BigQuery loading for both JSON and CSV files
- Supports schema auto-detection and partitioning by date column
- Feature flag `ENABLE_BQ=true` implemented for optional deployment

---

## PR 9: Looker Studio Extract Config (Cached Dataset)  
**Branch:** `feature/looker-extract-config`  
- [ ] Add `config/looker_extract_klaviyo.json` – template for Google "Extract Data" connector  
- [ ] Pre‑filters: last 90 days, aggregate by **Campaign ID** + **Date**  
- [ ] Document step‑by‑step import instructions in `docs/looker_extract_setup.md`  
- [ ] Include screenshot placeholders (saved as `/docs/img/…`)  

**Validation**  
1. Dev ► Import JSON into Looker Studio; verify extract created without errors  
2. Reviewer ► Confirm row count ≤100 MB limit and fields align with mock dataset  
3. Reviewer ► Ensure doc steps are reproducible on fresh account  

---

## PR 10: Data‑Volume Performance Tests  
**Branch:** `feature/perf-tests`  
- [ ] Create `tests/perf/test_query_limits.py` – measures fetch time & rows for 1‑, 7‑, 30‑day ranges  
- [ ] Use pytest marker `@perf` to exclude from default suite  
- [ ] Output summary CSV `perf_results.csv` (query, rows, seconds, success flag)  
- [ ] Add GitHub Action workflow `ci-perf.yml` (manual trigger) to run perf tests weekly  

**Validation**  
1. Dev ► Run `pytest -m perf` locally; verify results file produced  
2. Reviewer ► Check thresholds: 1‑day <60 s, 7‑day <300 s on sample data  
3. Reviewer ► Confirm CI workflow succeeds and uploads artifact  

---

## Implementation Notes (for PRs 7–10)  
* Continue using the directory structure defined in the original plan.  
* PR 7 output becomes an accepted input path for the existing **ETL Runner** (PR 5) – do **not** refactor ETL yet; just ensure compatibility.  
* PR 8 is optional in the MVP demo but prepares for scale; gate deployment behind `ENABLE_BQ=true`.  
* Keep unit tests fast (<5 s each); mark integration/perf tests separately.  

---
