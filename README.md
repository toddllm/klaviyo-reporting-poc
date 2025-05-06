# Klaviyo Reporting POC

This repository contains tools for generating realistic mock data in Klaviyo to power reporting demos, test automations, and showcase value to clients. It also includes a narrow scope POC for automating Klaviyo report generation via Looker Studio.

## Workflow

![Klaviyo Reporting Workflow](docs/img/flow.svg)

## Features

- **Mock List Creation**: Creates a test list named `Mock_Reporting_List`
- **Mock Profile Generation**: Adds 20-30 realistic but fictional profiles to the list
- **Campaign Activity Simulation**: Simulates events for two mock campaigns
- **Flow Events Simulation**: Creates a mock welcome flow with message interactions
- **Purchase Behavior Simulation**: Generates realistic purchase events with product data
- **Automated Reporting**: Extracts campaign metrics from Klaviyo API and prepares them for Looker Studio

## Requirements

- Python 3.6+
- Python version managed with `pyenv` (see `.python-version`; Python 3.10.6)
- Required packages: `requests`, `faker`, `python-dotenv` (see requirements.txt)
- Klaviyo API key (stored in private-api-key.txt or as environment variable)
- Looker Studio account (for visualization)

## API Version

- All scripts use Klaviyo API revision **2025-04-15**
- See [API Usage Guidelines](docs/api_usage.md) for important information about API versioning and edge cases
- TODO: Make API revision an environment variable to simplify future updates

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and update with your values:

```bash
KLAVIYO_API_KEY=pk_xxx
AUDIENCE_ID=YdSN6t
CAMPAIGN_ID=AbCdEf
TEMPLATE_ID=WJ3kbV
NUM_TEST_PROFILES=5
MODE=mock  # Use 'real' for actual API calls
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_WEBHOOK
LOOKER_REPORT_URL=https://datastudio.google.com/reporting/YOUR_REPORT_ID
```

Alternatively, you can set these as environment variables in your system.

## Mock Data Generation

### Usage

1. Set up your environment variables (either in `.env` file or system environment)
2. Run the script:

```bash
python mock_klaviyo_reporting_data.py
```

Alternatively, you can still use the legacy method:

1. Ensure your Klaviyo API key is in `private-api-key.txt` (should start with `pk_`)
2. Run the script as above

### Sending Reports to Slack

To send campaign performance reports to Slack:

```bash
python slack_integration.py
```

This will format the metrics and insights into a nicely formatted Slack message with links to the Looker Studio dashboard.

### What Gets Created

1. **List**: `Mock_Reporting_List` with 25 profiles
2. **Campaigns**:
   - `Mock_Welcome_Campaign`
   - `Mock_Product_Update`
3. **Flow**: `Mock_Welcome_Flow`
4. **Events**:
   - Campaign events: `Email Opened`, `Email Clicked`, `Unsubscribed`
   - Flow events: `Flow Email Sent`, `Flow Email Opened`
   - Purchase events: `Placed Order` with product details
5. **Integrations**:
   - Slack notifications with campaign performance metrics
   - Links to Looker Studio dashboards

## Narrow Scope POC

A narrowed scope POC has been implemented to focus specifically on automating Klaviyo report generation via Looker Studio using direct Klaviyo APIs. This implementation includes:

- **klaviyo_api_ingest.py**: Extracts campaign metrics from the Klaviyo API
- **lookml_field_mapper.py**: Normalizes Klaviyo fields to match Looker Studio schema
- **etl_runner.py**: Integrates the fetch → normalize → export pipeline
- **mock_looker_dataset.csv**: Mock dataset for testing visualizations
- **test_visualization_stub.json**: Sample Looker Studio configuration

For detailed information on the narrow scope POC, see [README-NARROW-SCOPE-POC.md](README-NARROW-SCOPE-POC.md).

### Running the Narrow Scope POC

```bash
# Run the full ETL pipeline
python src/etl_runner.py --output klaviyo_metrics.csv

# Or run individual components
python src/klaviyo_api_ingest.py --output campaigns.csv
python src/lookml_field_mapper.py
```

See the [Narrow Scope POC Documentation](README-NARROW-SCOPE-POC.md) for more details.

## Notes

- All mock data is clearly marked with `Mock_` prefixes
- No real emails are sent during this process
- Events are distributed across profiles with randomized timestamps
- Purchase data includes realistic product names, quantities, and prices

## Troubleshooting

If you encounter API errors:

- Verify your API key is correct and has proper permissions
- Check that the key in private-api-key.txt doesn't have trailing whitespace
- The script includes rate limiting to avoid overwhelming the Klaviyo API
- If API calls are failing, check if the API revision (2025-04-15) is still supported

## Known Limitations

- The current implementation only supports basic campaign metrics (open rate, click rate)
- No authentication for Looker Studio integration (manual upload required)
- Limited error handling for API rate limits
- No automated scheduling of data refresh

## Security

- The script reads the API key from a separate file for security
- No real customer data is used or modified
- No actual emails are sent to anyone

## Development

⚠️ **IMPORTANT: All developers must follow the Narrow Scope POC PR Plan** ⚠️

This project follows a structured development process outlined in the
[Narrow Scope POC PR Plan](docs/NARROW_SCOPE_POC_PR_PLAN.md). Before creating any PRs or making changes,
please review this document.

All PRs must:

1. Reference the PR Plan in the description
2. Include the PR number and title from the plan in your PR title
3. Align with one of the items in the plan

Do not create PRs that are not part of the plan without discussing with the team
first.

For a complete guide on working with this repository, please refer to the [START-HERE.md](START-HERE.md) file.
