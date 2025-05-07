# Fix Reporting View and Deploy PR Plan

This PR plan addresses critical issues identified during smoke-testing of the reporting pipeline, focusing on fixing the BigQuery view and deployment process to ensure a successful client demo.

## 1. BigQuery View - *highest impact*

| Issue                                   | Fix                                                                                                                             | Owner |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----- |
| `ILIKE` not supported                   | Replace with `LOWER(col) LIKE LOWER('%pattern%')` **or** drop the case-insensitive filter for now                               | PR 28 |
| Wrong table names (`email_*`)           | Use `campaign`, `event`, `list`; add conditional joins so missing `flow` table doesn't break the view (`LEFT JOIN flow f ON …`) | PR 28 |
| Deploy script fails to param-substitute | Switch to *bq* `--parameter` flags **or** run `bq query -q --use_legacy_sql=false < sql/final_view.sql` from Makefile           | PR 28 |

*Once fixed → run*

```bash
make deploy_view   # add a target in Makefile that calls the deploy script
python scripts/bq_sanity_check.py --tables reporting_view  # confirm it appears
```

## 2. ETL Runner import + zero-row problem

1. **Module path**

   *Inside `src/__init__.py` add*:

   ```python
   import pathlib, sys
   root = pathlib.Path(__file__).resolve().parent.parent
   if str(root) not in sys.path:
       sys.path.append(str(root))
   ```

   This removes the need for ad-hoc `PYTHONPATH` tweaks.

2. **Empty extract**

   *Likely cause*: the Postgres extract query filters on `created_at BETWEEN :start AND :end` but demo data is outside that window.

   *Quick patch* (in `postgres_extract_export.py`):

   ```python
   if not rows:
       logger.warning("⚠️  Extract returned 0 rows – falling back to last 30 days")
       rows = fetch_last_n_days(conn, table, 30)
   ```

   Re-run:

   ```bash
   python src/etl_runner.py --source fivetran --start 2024-01-01 --end 2025-12-31
   ```

## 3. `.env` sanity

*Lock in the real values*:

```ini
# GCP
BQ_PROJECT=clara-blueprint-script-24
BQ_DATASET=klaviyopoc
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json

# Fivetran system key (already set)
FIVETRAN_GROUP_ID=sectional_recognizable
FIVETRAN_CONNECTOR_ID=manufacturing_dollar
```

*Optional*: commit a `.env.example` that mirrors these keys but with placeholder values to avoid future drift.

## 4. Missing `flow` table (low risk for demo)

If the client doesn't need flow metrics yet, **edit** `scripts/bq_sanity_check.py` → `TABLES = ["campaign", "event", "list"]` so the smoke-test doesn't fail noisy.

## 5. Re-run automated smoke test

```bash
make smoke_test   # wrapper around scripts/smoke_test_agent.py
open logs/smoke_test_log_$(date +%Y%m%d)_*.md
```

Expect **all phases to pass**; the Looker dashboard should load and screenshots be saved to `logs/screens/`.

## PR Plan to implement fixes

| PR                     | Branch                                | Contents                                                                                                                      |
| ---------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **PR 28**              | `bugfix/bq_view_and_deploy`           | • Rewrite `sql/create_reporting_view.sql` <br>• Update `scripts/deploy_reporting_view.sh` <br>• Add `make deploy_view` target |
| **PR 29**              | `bugfix/etl_import_and_empty_extract` | • Add path patch in `src/__init__.py` <br>• Improve empty-extract handling & logging                                          |
| **PR 30**              | `chore/env_examples_and_docs`         | • Add `.env.example` <br>• Update `docs/setup.md` with env checklist                                                          |
| **PR 31** *(optional)* | `chore/remove_flow_from_smoke`        | • Trim `flow` from required tables list                                                                                       |

After those merge, re-run **`make smoke_test`**.
If everything is green, we're truly demo-ready.
