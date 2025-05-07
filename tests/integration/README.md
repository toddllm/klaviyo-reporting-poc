# Integration Tests

This directory contains integration tests for the Klaviyo Reporting POC.

## Running the Tests

### Prerequisites

- Docker and Docker Compose installed
- Python environment with all dependencies installed

### Steps

1. Start the Docker containers:

```bash
cd tests/integration
docker-compose up -d
```

2. Run the integration tests:

```bash
pytest tests/integration/test_postgres_extract_export.py -v
```

3. Shut down the Docker containers when done:

```bash
cd tests/integration
docker-compose down
```

### Environment Variables

The integration tests use the following environment variables:

- `PG_HOST`: Postgres host (default: localhost)
- `PG_PORT`: Postgres port (default: 5432)
- `PG_DB`: Postgres database name (default: postgres)
- `PG_USER`: Postgres username (default: postgres)
- `PG_PASSWORD`: Postgres password (default: postgres)

### Skipping Integration Tests

To skip integration tests (e.g., in CI environments without Docker), set the `SKIP_INTEGRATION_TESTS` environment variable:

```bash
SKIP_INTEGRATION_TESTS=1 pytest
```
