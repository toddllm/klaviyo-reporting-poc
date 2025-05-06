# Mock Looker Dataset

This directory contains mock datasets for testing and development purposes.

## mock_looker_dataset.csv

This file contains mock data that simulates Klaviyo campaign metrics in a format compatible with Looker Studio.

### Fields

- `date`: The date of the campaign in YYYY-MM-DD format
- `campaign_name`: The name of the campaign
- `send_time`: The time the campaign was sent in ISO 8601 format
- `open_rate`: The open rate as a decimal (e.g., 0.42 for 42%)
- `click_rate`: The click rate as a decimal (e.g., 0.18 for 18%)
- `subject_line`: The subject line of the campaign
- `list_id`: The ID of the list the campaign was sent to

### Usage

#### Loading in Python

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('data/mock_looker_dataset.csv')

# Display the first few rows
print(df.head())

# Get basic statistics
print(df.describe())
```

#### Importing into Looker Studio

1. Open Looker Studio (https://lookerstudio.google.com/)
2. Click "Create" and select "Data Source"
3. Select "File Upload" as the connector
4. Upload `mock_looker_dataset.csv`
5. Verify field types and click "Connect"
6. Create a new report using this data source

### Data Generation

This mock dataset was generated to represent realistic campaign metrics over a three-month period (April-June 2025). The data includes:

- Weekly newsletters
- Special promotions
- Customer engagement campaigns
- Month-end recap emails

The open rates and click rates are based on industry averages for email marketing campaigns.
