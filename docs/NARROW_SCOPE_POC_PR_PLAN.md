# Narrow Scope POC PR Plan

⚠️ **IMPORTANT: ALL DEVELOPERS MUST FOLLOW THIS PLAN** ⚠️

This document outlines the specific PRs that should be created for implementing the narrow scope POC as described in `narrow-scope-POC.md`. Each PR should be implemented one at a time, with clear validation steps for both developers and reviewers.

**REQUIRED ACTIONS FOR ALL DEVELOPERS:**

1. **REFERENCE THIS PLAN IN EVERY PR DESCRIPTION** with a link to this document
2. **INCLUDE THE PR NUMBER AND TITLE FROM THIS PLAN** in your PR title
3. **ENSURE YOUR PR ALIGNS WITH ONE OF THE ITEMS BELOW**

**DO NOT create PRs that are not part of this plan without discussing with the team first.**

**EXAMPLE PR TITLE:** "PR 1: Klaviyo API Ingest Script"

**EXAMPLE PR DESCRIPTION START:**
```
Implements PR #1 from the [Narrow Scope POC PR Plan](../docs/NARROW_SCOPE_POC_PR_PLAN.md).

This PR adds the klaviyo_api_ingest.py script for fetching campaign metrics from the Klaviyo API.
```

---

## PR 1: Klaviyo API Ingest Script
**Branch:** feature/klaviyo-api-ingest
- [x] Create `src/klaviyo_api_ingest.py` for fetching campaign metrics from Klaviyo API
- [x] Implement API key authentication
- [x] Add functionality to fetch campaign list and associated metrics
- [x] Include pagination and error handling
- [x] Output data to a local CSV or JSON file
- [x] Add unit tests in `tests/test_klaviyo_api_ingest.py`

**Validation:**
1. Developer: Run `python src/klaviyo_api_ingest.py --dry-run` to verify API request format
2. Developer: Run unit tests with `pytest tests/test_klaviyo_api_ingest.py`
3. Reviewer: Verify error handling for API failures
4. Reviewer: Confirm pagination works correctly for large result sets

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR merged on May 6, 2025
- All tests passing: `pytest tests/test_klaviyo_api_ingest.py`
- Implementation includes API key authentication, pagination, error handling, and CSV/JSON output

---

## PR 2: LookML Field Mapper
**Branch:** feature/lookml-field-mapper
- [x] Create `src/lookml_field_mapper.py` for normalizing Klaviyo fields
- [x] Implement mapping dictionary from raw Klaviyo field names to reporting-ready field names
- [x] Add unit tests in `tests/test_lookml_field_mapper.py`
- [x] Ensure the mapper can be reused in pipeline or mock data setup

**Validation:**
1. Developer: Run unit tests with `pytest tests/test_lookml_field_mapper.py`
2. Developer: Verify mapping works with sample Klaviyo API response
3. Reviewer: Check that all required fields are mapped correctly
4. Reviewer: Ensure edge cases are handled (missing fields, null values, etc.)

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality

**Evidence:**
- PR #35 merged on May 6, 2025
- All tests passing: `pytest tests/test_lookml_field_mapper.py`
- Implementation includes field mapping, date formatting, derived fields calculation, and error handling

---

## PR 3: Mock Looker Dataset
**Branch:** feature/mock-looker-dataset
- [x] Create `data/mock_looker_dataset.csv` with realistic mock data
- [x] Include fields: `date`, `campaign_name`, `send_time`, `open_rate`, `click_rate`, `subject_line`, `list_id`
- [x] Add at least 10 rows of realistic data
- [x] Add documentation on how to use the mock dataset

**Validation:**
1. Developer: Verify CSV format is correct and can be loaded with standard CSV libraries
2. Developer: Check that all required fields are present
3. Reviewer: Confirm data is realistic and representative
4. Reviewer: Validate that the CSV can be imported into Looker Studio

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] CSV format is valid
- [x] All required fields are present
- [x] Documentation is clear and complete

**Evidence:**
- PR merged on May 6, 2025
- CSV contains 16 rows of realistic campaign data
- All required fields are present and properly formatted
- Data spans April-June 2025 with varied metrics

---

## PR 4: Test Visualization Stub
**Branch:** feature/test-visualization-stub
- [x] Create `config/test_visualization_stub.json` with sample Looker Studio config
- [x] Define one line chart (open rate over time)
- [x] Define one bar chart (click rate by campaign)
- [x] Add comments explaining field requirements and naming assumptions

**Validation:**
1. Developer: Verify JSON is valid and well-formatted
2. Developer: Check that all required fields are referenced correctly
3. Reviewer: Confirm visualization config aligns with mock dataset
4. Reviewer: Validate that comments clearly explain field requirements

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] JSON is valid and well-formatted
- [x] Visualization config aligns with mock dataset
- [x] Comments are clear and helpful

**Evidence:**
- PR merged on May 6, 2025
- JSON is valid and well-formatted with comprehensive comments
- Configuration includes line chart for open rate over time and bar chart for click rate by campaign
- Implementation includes detailed field requirements and implementation notes

---

## PR 5: ETL Runner
**Branch:** feature/etl-runner
- [x] Create `src/etl_runner.py` to integrate fetch → normalize → export
- [x] Combine functionality from `klaviyo_api_ingest.py` and `lookml_field_mapper.py`
- [x] Implement consistent file output format
- [x] Add unit tests in `tests/test_etl_runner.py`
- [x] Include support for future Supermetrics integration

**Validation:**
1. Developer: Run `python src/etl_runner.py --dry-run` to verify end-to-end flow
2. Developer: Run unit tests with `pytest tests/test_etl_runner.py`
3. Reviewer: Verify error handling for each step of the ETL process
4. Reviewer: Confirm output format matches requirements for Looker Studio

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Code follows project style guidelines
- [x] Unit tests cover key functionality
- [x] ETL process handles errors gracefully

**Evidence:**
- PR #39 merged on May 6, 2025
- All tests passing: `pytest tests/test_etl_runner.py`
- Implementation includes ETL pipeline with extract, transform, and load functions
- Error handling implemented for each step of the ETL process
- Support for future Supermetrics integration included

---

## PR 6: README Updates
**Branch:** feature/readme-updates
- [x] Update README.md with information about the narrow scope POC
- [x] Add sections for Overview, Setup, How to Run, and Next Steps
- [x] Include examples of how to use each script
- [x] Document known limitations and future enhancements

**Validation:**
1. Developer: Verify all scripts are documented correctly
2. Developer: Check that setup instructions are clear and complete
3. Reviewer: Confirm examples work as described
4. Reviewer: Validate that documentation is clear and helpful

**Merge when these checkboxes are green:**
- [x] All validation steps passed
- [x] Documentation is clear and complete
- [x] Examples work as described
- [x] Known limitations are documented

**Evidence:**
- PR #41 created on May 6, 2025
- Documentation includes comprehensive README-NARROW-SCOPE-POC.md with detailed information
- Added src/README.md with usage instructions for each script
- Updated main README.md with narrow scope POC information and examples

---

## Implementation Notes

### Directory Structure
The narrow scope POC should follow this directory structure:
```
/
├── src/
│   ├── klaviyo_api_ingest.py
│   ├── lookml_field_mapper.py
│   ├── etl_runner.py
│   ├── supermetrics_klaviyo_pull.py  # PR 7
│   └── bq_loader.py                  # PR 8
├── tests/
│   ├── test_klaviyo_api_ingest.py
│   ├── test_lookml_field_mapper.py
│   ├── test_etl_runner.py
│   ├── test_supermetrics_klaviyo_pull.py  # PR 7
│   ├── test_bq_loader.py                  # PR 8
│   └── perf/
│       └── test_query_limits.py           # PR 10
├── data/
│   ├── mock_looker_dataset.csv
│   └── supermetrics_raw_YYYYMMDD.json     # PR 7 output
├── config/
│   ├── test_visualization_stub.json
│   └── looker_extract_klaviyo.json        # PR 9
├── docs/
│   └── looker_extract_setup.md            # PR 9
└── README.md
```

### Implementation Order
Implement the PRs in the order listed above. Each PR builds on the previous one, so it's important to follow the sequence.

For Phase 2 (PRs 7-10), the recommended implementation order is:
1. First implement PR 7 (Supermetrics → CSV Pull Script)
2. Then implement PR 8 (BigQuery Loader) and PR 9 (Looker Studio Extract Config) in parallel
3. Finally implement PR 10 (Data‑Volume Performance Tests) to validate the complete solution

### Testing Strategy

#### Phase 1 (PRs 1-6)
- Unit tests should be included for all Python scripts
- Mock API responses for testing `klaviyo_api_ingest.py`
- Test edge cases for field mapping in `lookml_field_mapper.py`
- Integration tests for `etl_runner.py` to verify end-to-end flow

#### Phase 2 (PRs 7-10)
- Mock Supermetrics API responses for testing `supermetrics_klaviyo_pull.py`
- Use BigQuery emulator for testing `bq_loader.py`
- Separate performance tests with pytest markers to avoid slowing down the regular test suite
- Implement CI workflow for automated performance testing

### Documentation

#### Phase 1 (PRs 1-6)
- Add docstrings to all functions
- Include examples in README.md
- Document known limitations and future enhancements

#### Phase 2 (PRs 7-10)
- Create step-by-step guide for Looker Studio Extract setup
- Document BigQuery schema and partitioning strategy
- Include performance test results and recommendations
- Update main README.md with information about the extended functionality

> After each PR merge, assign a tester to follow the **Validation** steps and attach **Evidence**. Once all PRs are merged and validated, the narrow scope POC is ready for demonstration. 🚀

---

# Phase 2: Extended Functionality

*(The following PRs extend the Narrow Scope POC with additional features)*

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
- PR #45 merged on May 6, 2025
- All tests passing: `pytest tests/test_supermetrics_klaviyo_pull.py`
- Implementation includes API key authentication, pagination, error handling, and CSV/JSON output
- Dry run functionality works as expected

---

## PR 8: BigQuery Loader (Optional Warehouse Path)  
**Branch:** `feature/bq-loader`  
- [ ] Add `src/bq_loader.py` to load Supermetrics‐generated CSV/JSON into BigQuery table `klaviyo_raw.events`  
- [ ] Use `google-cloud-bigquery` client; creds via service‑account JSON  
- [ ] Schema auto‑detect + partition by `date` column  
- [ ] Add CI step `pytest tests/test_bq_loader.py` with BigQuery emulator (or mock)  

**Validation**  
1. Dev ► Load sample file from PR 7 into a local/emulated BQ instance  
2. Dev ► Query table; ensure row count matches source file  
3. Reviewer ► Confirm partitioning & clustering flags set  
4. Reviewer ► Check idempotency (re‑running loader does not duplicate rows)  

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Code follows project style guidelines
- [ ] Unit tests cover key functionality

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

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] JSON is valid and well-formatted
- [ ] Documentation is clear and complete

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

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Tests are properly marked and isolated
- [ ] CI workflow is correctly configured

---

## Implementation Notes (for PRs 7–10)  
* Continue using the directory structure defined in the original plan.  
* PR 7 output becomes an accepted input path for the existing **ETL Runner** (PR 5) – do **not** refactor ETL yet; just ensure compatibility.  
* PR 8 is optional in the MVP demo but prepares for scale; gate deployment behind `ENABLE_BQ=true`.  
* Keep unit tests fast (<5 s each); mark integration/perf tests separately.
