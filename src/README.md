# Source Code

This directory contains the source code for the Klaviyo Reporting POC.

## Files

### klaviyo_api_ingest.py

This script is responsible for extracting campaign metrics from the Klaviyo API.

**Usage:**
```bash
python klaviyo_api_ingest.py --output campaigns.csv
```

**Options:**
- `--dry-run`: Perform a dry run without making actual API calls
- `--output`: Specify the output file path (default: campaigns.csv)
- `--format`: Specify the output format (csv or json, default: csv)

### lookml_field_mapper.py

This script normalizes Klaviyo fields to match the expected schema for Looker Studio visualizations.

**Usage:**
```bash
python lookml_field_mapper.py
```

This script is primarily used as a module by other scripts, but can be run standalone to see example transformations.

### etl_runner.py

This script integrates the fetch u2192 normalize u2192 export pipeline.

**Usage:**
```bash
python etl_runner.py --output klaviyo_metrics.csv
```

**Options:**
- `--dry-run`: Perform a dry run without making actual API calls
- `--output`: Specify the output file path (default: output/klaviyo_metrics_TIMESTAMP.csv)
- `--format`: Specify the output format (csv or json, default: csv)
