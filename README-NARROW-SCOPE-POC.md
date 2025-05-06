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
