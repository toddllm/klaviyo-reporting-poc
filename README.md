# Klaviyo Mock Reporting Data Generator

This script generates realistic mock data in Klaviyo to power reporting demos, test automations, and showcase value to clients.

## Features

- **Mock List Creation**: Creates a test list named `Mock_Reporting_List`
- **Mock Profile Generation**: Adds 20-30 realistic but fictional profiles to the list
- **Campaign Activity Simulation**: Simulates events for two mock campaigns
- **Flow Events Simulation**: Creates a mock welcome flow with message interactions
- **Purchase Behavior Simulation**: Generates realistic purchase events with product data

## Requirements

- Python 3.6+
- Required packages: `requests`, `faker`, `python-dotenv` (see requirements.txt)
- Klaviyo API key (stored in private-api-key.txt or as environment variable)

## API Version

> ⚠️ **IMPORTANT:** All API requests **must** include the `Klaviyo-Api-Version: 2025-04-15` header

- All scripts use Klaviyo API revision **2025-04-15**
- See [API Usage Guidelines](docs/api_usage.md) for important information about API versioning and edge cases
- Missing this header is a common cause of unexpected API behavior and errors
- TODO: Make API revision an environment variable to simplify future updates

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and update with your values:

```
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

## Usage

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

## What Gets Created

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

## Security

- The script reads the API key from a separate file for security
- No real customer data is used or modified
- No actual emails are sent to anyone

## Development

⚠️ **IMPORTANT: All developers must follow the GitHub PR Plan** ⚠️

This project follows a structured development process outlined in the [GitHub PR Plan](docs/GITHUB_PR_PLAN.md). Before creating any PRs or making changes, please review this document.

All PRs must:
1. Reference the PR Plan in the description
2. Include the PR number and title from the plan in your PR title
3. Align with one of the items in the plan

Do not create PRs that are not part of the plan without discussing with the team first.
