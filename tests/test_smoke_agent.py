import pathlib
import pytest
import os

# Import the agent module
import scripts.smoke_test_agent as agent

# Dummy datetime class to fix timestamps
def dummy_now():
    class D:
        def strftime(self, fmt):
            return '20210101_000000'
    return D()

@pytest.fixture(autouse=True)
def setup_env(tmp_path, monkeypatch):
    # Change working dir to tmp_path
    monkeypatch.chdir(tmp_path)
    # Create a minimal .env file
    env = tmp_path / '.env'
    env.write_text("\n".join([
        'FIVETRAN_SYSTEM_KEY=key',
        'FIVETRAN_SECRET=secret',
        'FIVETRAN_GROUP_ID=gid',
        'FIVETRAN_CONNECTOR_ID=cid',
        'BQ_PROJECT=proj',
        'BQ_DATASET=ds',
        'GOOGLE_SHEET_ID=sheetid',
        'GOOGLE_SHEET_NAME=sheetname',
        'GOOGLE_SHEET_RANGE_NAME=range',
        'LOOKER_SA_EMAIL=sa@example.com',
    ]))
    # Set required env vars for URLs
    monkeypatch.setenv('LOOKER_DASHBOARD_URL', 'http://example.com')
    monkeypatch.setenv('GOOGLE_SHEET_URL', 'http://example.com')
    # Monkeypatch datetime for deterministic names
    monkeypatch.setattr(agent.datetime, 'datetime', type('E', (), {'now': staticmethod(dummy_now)}) )
    yield


def test_smoke_agent_dry_run(monkeypatch):
    # Mock phase functions to always pass
    monkeypatch.setattr(agent, 'check_pre_flight', lambda dry: (True, 'ok'))
    monkeypatch.setattr(agent, 'check_fivetran_sync', lambda dry: (True, 'ok'))
    monkeypatch.setattr(agent, 'check_bigquery', lambda: (True, 'ok'))
    monkeypatch.setattr(agent, 'check_etl_runner', lambda dry: (True, 'ok'))
    monkeypatch.setattr(agent, 'deploy_bq_view', lambda: (True, 'ok'))
    monkeypatch.setattr(agent, 'check_looker_dashboard', lambda dry: (True, 'ok', None))
    monkeypatch.setattr(agent, 'check_google_sheet', lambda dry: (True, 'ok', None))

    # Run agent in dry-run mode
    with pytest.raises(SystemExit) as exc:
        agent.main(['--dry-run'])
    assert exc.value.code == 0

    # Assert log file created
    logs = pathlib.Path('logs')
    files = sorted(logs.glob('smoke_test_log_*.md'))
    assert len(files) == 1
    content = files[0].read_text()
    assert 'Phase 0' in content
    assert '✅ PASS' in content 