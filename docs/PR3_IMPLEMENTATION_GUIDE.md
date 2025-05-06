# PR 3: Mock Looker Dataset - Implementation Guide

This guide provides detailed instructions for creating the `mock_looker_dataset.csv` file as part of PR 3 in the Narrow Scope POC PR Plan.

## Overview

The `mock_looker_dataset.csv` file is a mock dataset that simulates Klaviyo export data with the fields expected by Looker Studio. It should:

1. Include all required fields: `date`, `campaign_name`, `send_time`, `open_rate`, `click_rate`, `subject_line`, `list_id`
2. Contain at least 10 rows of realistic data
3. Be formatted correctly for import into Looker Studio
4. Include documentation on how to use the mock dataset

## Implementation Steps

### 1. Create the Directory Structure

Create the `data` directory if it doesn't exist:

```bash
mkdir -p data
```

### 2. Create the Mock Dataset

Create a new file at `data/mock_looker_dataset.csv` with the following content:

```csv
date,campaign_name,send_time,open_rate,click_rate,subject_line,list_id
2025-04-01,April Newsletter,2025-04-01T09:00:00Z,0.42,0.18,"April Updates and Promotions",list_123
2025-04-08,Product Launch,2025-04-08T10:30:00Z,0.51,0.27,"Introducing Our New Product Line",list_123
2025-04-15,Mid-Month Special,2025-04-15T08:45:00Z,0.38,0.15,"Limited Time Offer: 25% Off",list_123
2025-04-22,Customer Appreciation,2025-04-22T11:15:00Z,0.47,0.22,"Thank You for Being a Loyal Customer",list_123
2025-04-29,April Recap,2025-04-29T09:30:00Z,0.44,0.19,"April Highlights and May Preview",list_123
2025-05-01,May Newsletter,2025-05-01T09:00:00Z,0.45,0.20,"May Updates and Promotions",list_123
2025-05-08,Spring Sale,2025-05-08T10:30:00Z,0.53,0.29,"Spring Sale: Up to 40% Off",list_123
2025-05-15,Mid-Month Special,2025-05-15T08:45:00Z,0.39,0.16,"Limited Time Offer: Free Shipping",list_123
2025-05-22,Customer Feedback,2025-05-22T11:15:00Z,0.48,0.23,"We Value Your Feedback",list_123
2025-05-29,May Recap,2025-05-29T09:30:00Z,0.46,0.21,"May Highlights and June Preview",list_123
2025-06-01,June Newsletter,2025-06-01T09:00:00Z,0.44,0.19,"June Updates and Promotions",list_456
2025-06-08,Summer Sale,2025-06-08T10:30:00Z,0.52,0.28,"Summer Sale: Up to 50% Off",list_456
2025-06-15,Mid-Month Special,2025-06-15T08:45:00Z,0.40,0.17,"Limited Time Offer: Buy One Get One",list_456
2025-06-22,Customer Appreciation,2025-06-22T11:15:00Z,0.49,0.24,"Thank You for Being a Loyal Customer",list_456
2025-06-29,June Recap,2025-06-29T09:30:00Z,0.47,0.22,"June Highlights and July Preview",list_456
```

### 3. Create Documentation

Create a new file at `data/README.md` with the following content:

```markdown
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
```

### 4. Create a Python Script to Generate the Dataset (Optional)

For future updates or to generate more data, you can create a script at `src/generate_mock_dataset.py`:

```python
#!/usr/bin/env python3
import csv
import random
from datetime import datetime, timedelta
import os

def generate_mock_dataset(num_rows=15, output_file="data/mock_looker_dataset.csv"):
    """Generate a mock dataset for Looker Studio"""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define campaign types and their typical metrics
    campaign_types = [
        {"name": "Newsletter", "open_rate": (0.40, 0.45), "click_rate": (0.18, 0.22)},
        {"name": "Product Launch", "open_rate": (0.48, 0.55), "click_rate": (0.25, 0.30)},
        {"name": "Sale", "open_rate": (0.50, 0.58), "click_rate": (0.26, 0.32)},
        {"name": "Mid-Month Special", "open_rate": (0.36, 0.42), "click_rate": (0.14, 0.18)},
        {"name": "Customer Appreciation", "open_rate": (0.45, 0.50), "click_rate": (0.20, 0.25)},
        {"name": "Recap", "open_rate": (0.42, 0.48), "click_rate": (0.18, 0.23)}
    ]
    
    # Define subject line templates
    subject_templates = [
        "{month} Updates and Promotions",
        "Introducing Our New Product Line",
        "{season} Sale: Up to {discount}% Off",
        "Limited Time Offer: {offer}",
        "Thank You for Being a Loyal Customer",
        "{month} Highlights and {next_month} Preview"
    ]
    
    # Define offers
    offers = ["25% Off", "Free Shipping", "Buy One Get One", "Gift with Purchase"]
    
    # Define seasons
    seasons = ["Spring", "Summer", "Fall", "Winter"]
    
    # Define discounts
    discounts = [20, 25, 30, 40, 50]
    
    # Define list IDs
    list_ids = ["list_123", "list_456"]
    
    # Generate data
    rows = []
    start_date = datetime(2025, 4, 1)  # Start from April 1, 2025
    
    for i in range(num_rows):
        # Calculate date (weekly campaigns)
        date = start_date + timedelta(days=i * 7)
        month = date.strftime("%B")
        next_month_date = date + timedelta(days=30)
        next_month = next_month_date.strftime("%B")
        
        # Determine season based on month
        month_num = date.month
        if 3 <= month_num <= 5:
            season = "Spring"
        elif 6 <= month_num <= 8:
            season = "Summer"
        elif 9 <= month_num <= 11:
            season = "Fall"
        else:
            season = "Winter"
        
        # Select campaign type
        campaign_type = random.choice(campaign_types)
        
        # Generate campaign name
        if i % 4 == 0:  # Monthly newsletter
            campaign_name = f"{month} Newsletter"
        elif i % 4 == 2:  # Mid-month special
            campaign_name = "Mid-Month Special"
        elif i % 4 == 3:  # Month-end recap
            campaign_name = f"{month} Recap"
        else:  # Other campaign
            campaign_name = f"{season} {campaign_type['name']}"
        
        # Generate subject line
        subject_template = random.choice(subject_templates)
        subject_line = subject_template.format(
            month=month,
            next_month=next_month,
            season=season,
            discount=random.choice(discounts),
            offer=random.choice(offers)
        )
        
        # Generate metrics
        open_rate = round(random.uniform(*campaign_type["open_rate"]), 2)
        click_rate = round(random.uniform(*campaign_type["click_rate"]), 2)
        
        # Generate send time (morning between 8am and noon)
        hour = random.randint(8, 11)
        minute = random.choice([0, 15, 30, 45])
        send_time = date.replace(hour=hour, minute=minute).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Select list ID
        list_id = list_ids[0] if date.month < 6 else list_ids[1]
        
        # Create row
        row = {
            "date": date.strftime("%Y-%m-%d"),
            "campaign_name": campaign_name,
            "send_time": send_time,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "subject_line": subject_line,
            "list_id": list_id
        }
        
        rows.append(row)
    
    # Write to CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated {len(rows)} rows of mock data in {output_file}")
    return rows

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate mock dataset for Looker Studio")
    parser.add_argument("--rows", type=int, default=15, help="Number of rows to generate")
    parser.add_argument("--output", default="data/mock_looker_dataset.csv", help="Output file path")
    args = parser.parse_args()
    
    generate_mock_dataset(args.rows, args.output)

if __name__ == "__main__":
    main()
```

## Validation Steps

### For Developers

1. Create the `data` directory if it doesn't exist:
   ```bash
   mkdir -p data
   ```

2. Create the `mock_looker_dataset.csv` file as described above.

3. Create the documentation in `data/README.md` as described above.

4. (Optional) Create the `generate_mock_dataset.py` script for future updates.

5. Verify that the CSV file is formatted correctly:
   ```bash
   head -n 5 data/mock_looker_dataset.csv
   ```

6. Verify that the CSV file can be loaded in Python:
   ```python
   import pandas as pd
   df = pd.read_csv('data/mock_looker_dataset.csv')
   print(df.head())
   ```

### For Reviewers

1. Verify that the CSV file contains all required fields:
   - `date`
   - `campaign_name`
   - `send_time`
   - `open_rate`
   - `click_rate`
   - `subject_line`
   - `list_id`

2. Verify that the CSV file contains at least 10 rows of realistic data.

3. Check that the data is formatted correctly for import into Looker Studio:
   - Dates are in YYYY-MM-DD format
   - Open rates and click rates are decimals (not percentages)
   - Subject lines are properly quoted if they contain commas

4. Verify that the documentation in `data/README.md` is clear and complete.

5. (Optional) Test importing the CSV file into Looker Studio to verify compatibility.

## Next Steps

After implementing and validating PR 3, proceed to PR 4: Test Visualization Stub.
