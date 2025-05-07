#!/usr/bin/env python3
"""
Automated Smoke-Test Agent
"""

import os
import sys
import subprocess
import argparse
import datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

console = Console()

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def write_log_header(md):
    md.write(f"# Smoke Test Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

def log_phase(md, phase, passed, commands, output, screenshot=None):
    status = "✅ PASS" if passed else "❌ FAIL"
    md.write(f"## {phase} - {status}\n\n")
    if commands:
        md.write("**Commands:**\n```\n")
        md.write("\n".join(commands))
        md.write("\n```\n\n")
    md.write("**Output:**\n```\n")
    md.write(output)
    md.write("\n```\n\n")
    if screenshot:
        rel = os.path.relpath(screenshot, Path.cwd())
        md.write(f"![{phase}]({rel})\n\n")

def check_pre_flight(dry_run):
    required = [
        "FIVETRAN_SYSTEM_KEY","FIVETRAN_SECRET","FIVETRAN_GROUP_ID","FIVETRAN_CONNECTOR_ID",
        "BQ_PROJECT","BQ_DATASET",
        "GOOGLE_SHEET_ID","GOOGLE_SHEET_NAME","GOOGLE_SHEET_RANGE_NAME",
        "LOOKER_SA_EMAIL",
        "LOOKER_DASHBOARD_URL","GOOGLE_SHEET_URL",
    ]
    if not Path('.env').exists():
        return False, ".env file not found"
    errors = []
    with open('.env') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    env = {l.split('=',1)[0]:l.split('=',1)[1] for l in lines if '=' in l}
    for k in required:
        v = env.get(k)
        if not v:
            errors.append(f"{k} missing or empty")
        elif v.startswith('"') or v.endswith('"') or v.strip()!=v:
            errors.append(f"{k} has quotes or whitespace")
    if errors:
        return False, "\n".join(errors)
    return True, "Environment OK"

def check_fivetran_sync(dry_run):
    cmds = ["python src/fivetran_connector_runner.py --dry-run"]
    code, out, err = run_command(cmds[0])
    if code != 0:
        return False, f"Dry-run failed: {err or out}"
    if dry_run:
        return True, out
    cmds.append("python src/fivetran_connector_runner.py")
    code2, out2, err2 = run_command(cmds[1])
    full = out + "\n" + out2 + "\n" + err2
    if code2 != 0 or "sync_completed: success" not in full:
        return False, full
    return True, full

def check_bigquery():
    cmd = "python scripts/bq_sanity_check.py"
    code, out, err = run_command(cmd)
    if code != 0 or "ERROR" in out or "ERROR" in err:
        return False, out + "\n" + err
    return True, out

def check_etl_runner(dry_run):
    start = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    end = datetime.date.today().isoformat()
    cmds = [f"python src/etl_runner.py --source fivetran --start {start} --end {end} --dry-run"]
    code, out, err = run_command(cmds[0])
    if code != 0 or "[DRY RUN]" not in out:
        return False, out + "\n" + err
    if dry_run:
        return True, out
    live_cmd = f"python src/etl_runner.py --source fivetran --start {start} --end {end}"
    cmds.append(live_cmd)
    code2, out2, err2 = run_command(live_cmd)
    full = out + "\n" + out2 + "\n" + err2
    if code2 != 0:
        return False, full
    return True, full

def deploy_bq_view():
    cmd = "bash scripts/deploy_reporting_view.sh"
    code, out, err = run_command(cmd)
    if code != 0 or ("View created" not in out and "already exists" not in out):
        return False, out + "\n" + err
    return True, out

def check_looker_dashboard(dry_run):
    url = os.environ.get("LOOKER_DASHBOARD_URL")
    if not url:
        return False, "LOOKER_DASHBOARD_URL not set", None
    if dry_run:
        return True, "Skipped screenshot", None
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    try:
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,'iframe')))
    except Exception as e:
        driver.quit()
        return False, str(e), None
    path = Path("logs/screens")/f"looker_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(path))
    driver.quit()
    return True, "Screenshot taken", path

def check_google_sheet(dry_run):
    url = os.environ.get("GOOGLE_SHEET_URL")
    if not url:
        return False, "GOOGLE_SHEET_URL not set", None
    if not dry_run:
        today = datetime.date.today().isoformat()
        subprocess.run(f"python scripts/sheets_push_snapshot.py --date {today}", shell=True)
    if dry_run:
        return True, "Skipped screenshot", None
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    try:
        WebDriverWait(driver,10).until(EC.title_contains("Google"))
    except Exception as e:
        driver.quit()
        return False, str(e), None
    path = Path("logs/screens")/f"sheet_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(path))
    driver.quit()
    return True, "Screenshot taken", path

def main(argv=None):
    parser = argparse.ArgumentParser(description="Automated Smoke-Test Agent")
    parser.add_argument("--dry-run", action="store_true", help="Skip live steps")
    args = parser.parse_args(argv)
    dry = args.dry_run
    Path("logs/screens").mkdir(parents=True, exist_ok=True)
    log_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path("logs")/f"smoke_test_log_{log_ts}.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "w") as md:
        write_log_header(md)
        p, detail = check_pre_flight(dry)
        log_phase(md, "Phase 0: Pre-flight", p, [], detail)
        if not p: sys.exit(1)
        p, detail = check_fivetran_sync(dry)
        log_phase(md, "Phase 1: Fivetran Sync", p, [], detail)
        if not p: sys.exit(1)
        p, detail = check_bigquery()
        log_phase(md, "Phase 2: BigQuery Sanity", p, [], detail)
        if not p: sys.exit(1)
        p, detail = check_etl_runner(dry)
        log_phase(md, "Phase 3: ETL Runner", p, [], detail)
        if not p: sys.exit(1)
        p, detail = deploy_bq_view()
        log_phase(md, "Phase 4: Deploy BQ View", p, [], detail)
        if not p: sys.exit(1)
        p, detail, shot = check_looker_dashboard(dry)
        log_phase(md, "Phase 5: Looker Dashboard", p, [], detail, shot)
        if not p: sys.exit(1)
        p, detail, shot = check_google_sheet(dry)
        log_phase(md, "Phase 6: Google Sheet", p, [], detail, shot)
        if not p: sys.exit(1)
    console.print(f"Smoke test completed. Log: {log_file}")
    sys.exit(0)

if __name__ == "__main__":
    main() 