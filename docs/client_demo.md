# Klaviyo Reporting Solution - Client Demo Guide

## Overview

This document provides a step-by-step guide for conducting a 15-minute Zoom demo of the Klaviyo Reporting Solution. The demo showcases the complete data pipeline from Klaviyo → Fivetran → BigQuery → Looker Studio, with an optional Google Sheets export.

## Prerequisites

- Access to the demo environment with all components set up
- Completed end-to-end demo run using `scripts/run_end_to_end_demo.sh`
- Client has been briefed on the purpose of the demo

## Demo Runsheet (15 minutes)

### 1. Introduction (2 minutes)

- Introduce yourself and the purpose of the demo
- Briefly explain the challenges of email marketing reporting
- Highlight the benefits of automated, centralized reporting

### 2. Solution Overview (3 minutes)

- Show the high-level architecture diagram
- Explain how data flows from Klaviyo to the reporting dashboard
- Emphasize the automated nature of the solution

### 3. Live Dashboard Demo (5 minutes)

- Open the Looker Studio dashboard
- Walk through each section of the dashboard:
  - Overall performance metrics (open rates, click rates, revenue)
  - Trend analysis over time
  - Campaign comparison
  - Detailed campaign metrics table
- Show how to filter by date range
- Demonstrate interactivity (hover, click, drill-down)

### 4. Google Sheets Export (Optional) (3 minutes)

- Show the Google Sheets export with the same metrics
- Explain how this can be shared with team members
- Highlight the automatic refresh capability

### 5. Next Steps and Q&A (2 minutes)

- Summarize the benefits of the solution
- Discuss implementation timeline and requirements
- Answer any questions

## One-Click Dashboard Setup

To provide clients with their own copy of the dashboard:

1. Share the "Make a copy" link: [Create your own dashboard](https://lookerstudio.google.com/reporting/create?c.reportId=DOCUMENT_ID)
2. When the client clicks the link, they'll be prompted to select a data source
3. They should select the BigQuery connection and the `v_email_metrics` view
4. The dashboard will automatically configure with all visualizations

## Troubleshooting

### Dashboard Shows "No Data"

- Verify that the BigQuery view has data
- Check that the client has proper permissions to the dataset
- Ensure the date filter is set to a range with data

### Visualizations Show Field Errors

- Confirm that the BigQuery view schema matches the expected fields
- Check for any renamed or missing columns
- Verify that the data types are correct

## Resources

- Dashboard Template JSON: `config/looker_dashboard.json`
- Dashboard Publishing Script: `scripts/publish_looker_template.sh`
- End-to-End Demo Script: `scripts/run_end_to_end_demo.sh`
- Client Slide Deck: `docs/client_deck.pdf`

## QR Codes

The slide deck includes QR codes for:

1. Looker Studio Dashboard Template
2. Google Sheets Template (if applicable)

These QR codes link directly to the "Make a copy" URLs for easy client access.
