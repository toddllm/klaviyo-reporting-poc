# Changelog

All notable changes to the Klaviyo Reporting POC will be documented in this file.

## [Unreleased]

### Added
- Comprehensive end-to-end demo documentation in `docs/END_TO_END_DEMO.md`
- Enhanced `run_end_to_end_demo.sh` script with improved error handling and additional options
- Mock data generation in `postgres_extract_export.py` for testing without database access
- Improved Fivetran connector integration with better error handling and authentication options
- Google Sheets snapshot functionality for quick data visualization
- `make demo` convenience target for running the end-to-end demo

### Changed
- Refactored SQL reporting view for better performance and readability
- Enhanced error handling and logging across all scripts
- Improved environment variable management and validation
- Updated smoke test agent with more comprehensive checks

### Fixed
- Fixed authentication issues with Fivetran API client
- Resolved path resolution issues in Python modules
- Improved error messages for missing environment variables

## [0.1.0] - 2025-05-06

### Added
- Initial release of Klaviyo Reporting POC
- Basic ETL pipeline from Klaviyo to BigQuery
- Fivetran connector integration
- BigQuery reporting view
- Looker Studio dashboard integration
