# Klaviyo Mock Reporting Data Generator

This repository contains scripts for generating realistic mock data in Klaviyo for reporting demos and testing.

## 📋 What Gets Created

1. **Lists**: 
   - `Mock_Reporting_List` with 25 mock profiles
   
2. **Events**:
   - **Flow Events**: `Flow Email Sent` and `Flow Email Opened`
   - **Purchase Events**: `Placed Order` with product details
   - All events include proper tracking properties and timestamps

3. **Profiles**:
   - Each profile has first name, last name, email, and location data
   - Emails follow `firstname.lastname.mock@example.com` pattern

## 🛠️ Scripts

### Main Script
- `mock_klaviyo_final.py` - Use this for generating mock data in Klaviyo

### Utility Scripts
- `validate.py` - Verifies what mock data exists in your Klaviyo account
- `cleanup.py` - Removes all mock data (lists, flows, campaigns with 'Mock_' prefix)

## 🚀 Usage

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Creating Mock Data

```bash
# Create mock data in Klaviyo
python mock_klaviyo_final.py
```

### Verifying Data

```bash
# Verify what's in your Klaviyo account
python validate.py
```

### Cleaning Up

```bash
# Remove all mock data
python cleanup.py
```

## 📝 Notes and Troubleshooting

### API Limitations

We encountered several API limitations during development:

1. **Campaign Creation**: The Klaviyo API has strict requirements for campaign creation that require additional setup beyond the scope of mock data generation. The script successfully tracks campaign-related events but doesn't create actual campaign objects.

2. **Flow Creation**: Similarly, flows can be complex to create via API. Our approach focuses on tracking flow-related events which is sufficient for reporting purposes.

3. **Event Verification**: The event validation is challenging because Klaviyo's reporting API works differently than the data creation API. The events are created successfully but may not appear immediately in the validation script.

### Validation

For best results, verify your mock data directly in the Klaviyo dashboard after running the script:

1. Log into your Klaviyo account
2. Check the Lists section for `Mock_Reporting_List` 
3. View the Activity Feed to see the tracked events
4. Check Metrics for events like `Flow Email Sent`, `Flow Email Opened`, and `Placed Order`

### Known Issues

- Campaign objects don't appear in the Klaviyo UI, but campaign-related events are tracked
- Phone numbers are not included due to Klaviyo's strict E.164 validation

### Best Practices

- Always run `cleanup.py` before generating new mock data to avoid duplication
- Wait a few minutes after data generation before running validation
- Use the Klaviyo dashboard for most accurate verification

## ✨ Next Steps

Future enhancements could include:

1. Support for additional event types
2. More complex purchase behaviors with product catalogs
3. Improved campaign and flow creation with templates
4. A comprehensive dashboard for monitoring mock data generation

## 🔒 Security

- The script reads the API key from a separate file for security
- No real customer data is used or modified
- No actual emails are sent to anyone
