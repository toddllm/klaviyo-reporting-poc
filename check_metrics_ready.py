#!/usr/bin/env python3

import argparse
import os
import sys
import json

def check_metrics_ready(mode="live"):
    """Check if metrics are ready by looking for metrics.json file
    and verifying it contains expected data."""
    # In mock mode, always return success for testing
    if mode == "mock":
        print("Mock mode: Metrics are ready")
        return True
    
    # Check if metrics.json exists
    if not os.path.exists("metrics.json"):
        print("Metrics file not found")
        return False
    
    # Check if metrics.json contains data
    try:
        with open("metrics.json", "r") as f:
            metrics_data = json.load(f)
        
        # Check if metrics data contains expected fields
        if not metrics_data or not isinstance(metrics_data, list) or len(metrics_data) == 0:
            print("Metrics data is empty or invalid")
            return False
        
        # Check if at least one metric has data
        for metric in metrics_data:
            if "data" in metric and metric["data"]:
                print("Metrics are ready")
                return True
        
        print("No metric data found")
        return False
    
    except Exception as e:
        print(f"Error checking metrics: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Check if metrics are ready")
    parser.add_argument("--mode", default="live", choices=["live", "mock"],
                        help="Mode to run in (live or mock)")
    
    args = parser.parse_args()
    
    if check_metrics_ready(args.mode):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
