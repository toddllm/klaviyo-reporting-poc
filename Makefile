# Klaviyo Reporting POC Makefile

.PHONY: deploy_view smoke_test demo

# Deploy BigQuery reporting view
deploy_view:
        @echo "Deploying BigQuery reporting view..."
        ./scripts/deploy_reporting_view.sh

# Run smoke test
smoke_test:
        @echo "Running smoke test..."
        python scripts/smoke_test_agent.py

# Run end-to-end demo
demo:
        @echo "Running end-to-end demo..."
        ./scripts/run_end_to_end_demo.sh
