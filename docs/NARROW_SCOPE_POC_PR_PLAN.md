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
- [ ] Update README.md with information about the narrow scope POC
- [ ] Add sections for Overview, Setup, How to Run, and Next Steps
- [ ] Include examples of how to use each script
- [ ] Document known limitations and future enhancements

**Validation:**
1. Developer: Verify all scripts are documented correctly
2. Developer: Check that setup instructions are clear and complete
3. Reviewer: Confirm examples work as described
4. Reviewer: Validate that documentation is clear and helpful

**Merge when these checkboxes are green:**
- [ ] All validation steps passed
- [ ] Documentation is clear and complete
- [ ] Examples work as described
- [ ] Known limitations are documented

---

## Implementation Notes

### Directory Structure
The narrow scope POC should follow this directory structure:
```
/
├── src/
│   ├── klaviyo_api_ingest.py
│   ├── lookml_field_mapper.py
│   └── etl_runner.py
├── tests/
│   ├── test_klaviyo_api_ingest.py
│   ├── test_lookml_field_mapper.py
│   └── test_etl_runner.py
├── data/
│   └── mock_looker_dataset.csv
├── config/
│   └── test_visualization_stub.json
└── README.md
```

### Implementation Order
Implement the PRs in the order listed above. Each PR builds on the previous one, so it's important to follow the sequence.

### Testing Strategy
- Unit tests should be included for all Python scripts
- Mock API responses for testing `klaviyo_api_ingest.py`
- Test edge cases for field mapping in `lookml_field_mapper.py`
- Integration tests for `etl_runner.py` to verify end-to-end flow

### Documentation
- Add docstrings to all functions
- Include examples in README.md
- Document known limitations and future enhancements

> After each PR merge, assign a tester to follow the **Validation** steps and attach **Evidence**. Once all PRs are merged and validated, the narrow scope POC is ready for demonstration. 🚀
