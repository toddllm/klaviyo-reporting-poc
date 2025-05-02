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
- Klaviyo API key (stored in private-api-key.txt)

## API Version

- All scripts use Klaviyo API revision **2025-04-15**
- TODO: Make API revision an environment variable to simplify future updates

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your Klaviyo API key is in `private-api-key.txt` (should start with `pk_`)
2. Run the script:

```bash
python mock_klaviyo_reporting_data.py
```

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
