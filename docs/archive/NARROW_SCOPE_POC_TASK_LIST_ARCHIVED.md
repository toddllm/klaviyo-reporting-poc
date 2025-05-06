# 🚀 Coding Agent Task List for Narrowed POC
**Date:** 2025-05-06

This document outlines the GitHub PRs needed to reach a working proof of concept (POC) for the narrowed scope of automating Klaviyo report generation via Looker Studio using Supermetrics or direct Klaviyo APIs. These are the foundational tasks that can be executed regardless of the final data source strategy.

---

## ✅ PR 1: `klaviyo_api_ingest.py`
**Purpose:** Create a basic data extraction script for Klaviyo API to fetch campaign metrics.

**Tasks:**
- Use API key auth.
- Fetch campaign list and associated metrics (`send_time`, `subject`, `open_rate`, `click_rate`, etc.).
- Output to a local CSV or JSON file.
- Include pagination and error handling.

---

## ✅ PR 2: `lookml_field_mapper.py`
**Purpose:** Normalize Klaviyo fields to match expected schema for Looker Studio visualizations.

**Tasks:**
- Create mapping dict from raw Klaviyo field names → reporting-ready field names.
- Include unit tests for transform logic.
- Can be reused in pipeline or mock data setup.

---

## ✅ PR 3: `mock_looker_dataset.csv`
**Purpose:** Create a known-good mock dataset that simulates Klaviyo export with the fields expected by Looker Studio.

**Fields to include:**
- `date`, `campaign_name`, `send_time`, `open_rate`, `click_rate`, `subject_line`, `list_id`

**Usage:**
- Allows local testing of visualizations or dashboards without waiting for real data flow.
- Enables QA and iteration of frontend elements and charting.

---

## ✅ PR 4: `test_visualization_stub.json`
**Purpose:** Stub out a sample Looker Studio JSON config that references the mock data fields.

**Tasks:**
- Define one line chart (open rate over time) and one bar chart (click rate by campaign).
- Comment which fields need to exist and naming assumptions.

---

## ✅ PR 5: `etl_runner.py`
**Purpose:** Glue logic to integrate fetch → normalize → export to file (eventually to Looker or Sheets).

**Tasks:**
- Combines `klaviyo_api_ingest.py` + `lookml_field_mapper.py`.
- Outputs a consistent file format.
- Lays the groundwork for plugging into Supermetrics if needed later.

---

## ✅ PR 6: `README.md`
**Purpose:** Explain the POC pipeline, how to run each script, and known limitations.

**Sections:**
- Overview
- Setup
- How to run
- Next steps
