import os
import subprocess
import sys

def run_seed():
    print("[CHAIN] Running seed_profiles.py...")
    result = subprocess.run([sys.executable, "seed_profiles.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("seed_profiles.py failed")

def run_send_and_report():
    print("[CHAIN] Running send_and_report.py...")
    result = subprocess.run([sys.executable, "send_and_report.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("send_and_report.py failed")

def run_ai_insights():
    print("[CHAIN] Running ai_insights.py...")
    result = subprocess.run([sys.executable, "ai_insights.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("ai_insights.py failed")

def main():
    run_seed()
    run_send_and_report()
    run_ai_insights()
    print("[CHAIN] All steps complete.")

if __name__ == "__main__":
    main()
