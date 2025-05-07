# Klaviyo Reporting POC Makefile

.PHONY: deploy_view smoke_test

# Deploy BigQuery reporting view
deploy_view:
	@echo "Deploying BigQuery reporting view..."
	./scripts/deploy_reporting_view.sh

# Run smoke test
smoke_test:
	@echo "Running smoke test..."
	python scripts/smoke_test_agent.py
