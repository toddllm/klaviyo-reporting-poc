# PR 6: README Updates - Implementation Guide

This guide provides detailed instructions for updating the README.md file as part of PR 6 in the Narrow Scope POC PR Plan.

## Overview

The README.md update should provide comprehensive documentation for the narrow scope POC. It should:

1. Add sections for Overview, Setup, How to Run, and Next Steps
2. Include examples of how to use each script
3. Document known limitations and future enhancements
4. Provide clear instructions for running the entire pipeline

## Implementation Steps

### 1. Create a Draft of the Updated README

Create a new file at `README-NARROW-SCOPE-POC.md` with the following content:

```markdown
# Klaviyo Reporting POC - Narrow Scope

This project implements a proof of concept (POC) for automating Klaviyo report generation via Looker Studio using direct Klaviyo APIs.

## Overview

The narrow scope POC focuses on the foundational tasks needed to extract campaign metrics from Klaviyo, normalize the data for reporting, and prepare it for visualization in Looker Studio.

### Components

- **klaviyo_api_ingest.py**: Extracts campaign metrics from the Klaviyo API
- **lookml_field_mapper.py**: Normalizes Klaviyo fields to match Looker Studio schema
- **etl_runner.py**: Integrates the fetch → normalize → export pipeline
- **mock_looker_dataset.csv**: Mock dataset for testing visualizations
- **test_visualization_stub.json**: Sample Looker Studio configuration

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Klaviyo API    │    │  Field Mapping  │    │  Output Files   │
│  (Extract)      │───>│  (Transform)    │───>│  (Load)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                                              │
        │                                              ▼
        │                                      ┌─────────────────┐
        │                                      │  Looker Studio  │
        └─────────────────────────────────────>│  Visualization  │
                                               └─────────────────┘
```

## Setup

### Prerequisites

- Python 3.6+ (Python 3.10.6 recommended, managed with `pyenv`)
- Klaviyo API key
- Looker Studio account (for visualization)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/klaviyo-reporting-poc.git
   cd klaviyo-reporting-poc
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Klaviyo API key and other settings
   ```

### Directory Structure

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

## How to Run

### Extract Data from Klaviyo

To fetch campaign metrics from the Klaviyo API:

```bash
python src/klaviyo_api_ingest.py --output campaigns.csv
```

Options:
- `--dry-run`: Perform a dry run without making actual API calls
- `--output`: Specify the output file path (default: campaigns.csv)
- `--format`: Specify the output format (csv or json, default: csv)

### Normalize Data

To normalize Klaviyo fields to match Looker Studio schema:

```bash
python src/lookml_field_mapper.py
```

This script is primarily used as a module by other scripts, but can be run standalone to see example transformations.

### Run the Full ETL Pipeline

To run the complete extract → transform → load pipeline:

```bash
python src/etl_runner.py --output klaviyo_metrics.csv
```

Options:
- `--dry-run`: Perform a dry run without making actual API calls
- `--output`: Specify the output file path (default: output/klaviyo_metrics_TIMESTAMP.csv)
- `--format`: Specify the output format (csv or json, default: csv)

### Using the Mock Dataset

For testing without connecting to the Klaviyo API, you can use the mock dataset:

```bash
cp data/mock_looker_dataset.csv output/klaviyo_metrics.csv
```

### Visualizing in Looker Studio

1. Open Looker Studio (https://lookerstudio.google.com/)
2. Click "Create" and select "Data Source"
3. Select "File Upload" as the connector
4. Upload the output CSV file (e.g., `klaviyo_metrics.csv`)
5. Verify field types and click "Connect"
6. Create a new report using this data source
7. Add charts as described in `config/test_visualization_stub.json`

## Testing

To run all tests:

```bash
python -m pytest
```

To run tests for a specific module:

```bash
python -m pytest tests/test_klaviyo_api_ingest.py
python -m pytest tests/test_lookml_field_mapper.py
python -m pytest tests/test_etl_runner.py
```

## Known Limitations

- The current implementation only supports basic campaign metrics (open rate, click rate)
- No authentication for Looker Studio integration (manual upload required)
- Limited error handling for API rate limits
- No automated scheduling of data refresh

## Next Steps

### Short Term

- Add support for additional metrics (revenue, unsubscribes, etc.)
- Implement automated data refresh via Google Sheets API
- Add support for filtering by date range and campaign type
- Improve error handling and retry logic

### Long Term

- Integrate with Supermetrics for additional data sources
- Implement automated scheduling via cron or cloud functions
- Add support for custom metrics and segments
- Create a web interface for configuring data extraction

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

### 2. Update the Main README.md

Update the main README.md file to include the narrow scope POC information. You can either replace the entire file with the content above or add a new section for the narrow scope POC.

If adding a new section, insert the following at an appropriate location in the existing README.md:

```markdown
## Narrow Scope POC

A narrowed scope POC has been implemented to focus specifically on automating Klaviyo report generation via Looker Studio using direct Klaviyo APIs. This implementation includes:

- **klaviyo_api_ingest.py**: Extracts campaign metrics from the Klaviyo API
- **lookml_field_mapper.py**: Normalizes Klaviyo fields to match Looker Studio schema
- **etl_runner.py**: Integrates the fetch → normalize → export pipeline
- **mock_looker_dataset.csv**: Mock dataset for testing visualizations
- **test_visualization_stub.json**: Sample Looker Studio configuration

For detailed information on the narrow scope POC, see [Narrow Scope POC Documentation](docs/NARROW_SCOPE_POC_PR_PLAN.md).

### Running the Narrow Scope POC

```bash
# Run the full ETL pipeline
python src/etl_runner.py --output klaviyo_metrics.csv

# Or run individual components
python src/klaviyo_api_ingest.py --output campaigns.csv
python src/lookml_field_mapper.py
```

See the [Narrow Scope POC Documentation](docs/NARROW_SCOPE_POC_PR_PLAN.md) for more details.
```

### 3. Create a README for the src Directory

Create a new file at `src/README.md` with the following content:

```markdown
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

This script integrates the fetch → normalize → export pipeline.

**Usage:**
```bash
python etl_runner.py --output klaviyo_metrics.csv
```

**Options:**
- `--dry-run`: Perform a dry run without making actual API calls
- `--output`: Specify the output file path (default: output/klaviyo_metrics_TIMESTAMP.csv)
- `--format`: Specify the output format (csv or json, default: csv)
```

## Validation Steps

### For Developers

1. Create the draft README at `README-NARROW-SCOPE-POC.md` as described above.

2. Update the main README.md file to include the narrow scope POC information.

3. Create the src/README.md file as described above.

4. Verify that all documentation is accurate and up-to-date.

5. Check for any broken links or references.

### For Reviewers

1. Verify that the documentation is clear, complete, and accurate.

2. Check that all scripts and their options are documented correctly.

3. Ensure that the setup instructions are clear and complete.

4. Verify that the known limitations and next steps are documented.

5. Check that the examples work as described.

## Next Steps

After implementing and validating PR 6, the narrow scope POC implementation is complete. The next steps would be to:

1. Integrate the narrow scope POC with the existing codebase
2. Implement the next steps described in the README
3. Expand the POC to include additional features and functionality
