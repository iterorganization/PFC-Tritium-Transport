#!/usr/bin/env python3
"""
Check status of SLURM job logs.

Reads the last lines of all .out files in the logs folder and reports:
- Number of completed simulations
- Number of failed/crashed simulations
- Number of currently running simulations
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def analyze_logs():
    """Analyze all .out files in logs folder and report status."""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("❌ logs folder not found")
        return
    
    # Get all .out files
    log_files = sorted(logs_dir.glob("*.out"))
    
    if not log_files:
        print("❌ No .out files found in logs folder")
        return
    
    # Status counters
    completed = []
    failed = []
    running = []
    error_details = defaultdict(int)
    
    # Analyze each log file
    for log_file in log_files:
        try:
            # Read last 100 lines to get status
            with open(log_file, 'r', errors='ignore') as f:
                lines = f.readlines()
            
            if not lines:
                running.append(log_file.name)
                continue
            
            # Check last lines for completion indicators
            last_content = ''.join(lines[-100:])
            
            # Check for success patterns
            if "✓ Simulation complete!" in last_content or "Simulation complete for bin" in last_content:
                completed.append(log_file.name)
            # Check for error/failure patterns
            elif "Error" in last_content or "error" in last_content or "FAILED" in last_content or "Traceback" in last_content:
                failed.append(log_file.name)
                # Extract error type
                if "Traceback" in last_content:
                    error_type = "Python Exception"
                    # Try to get the exception type
                    for line in lines[-20:]:
                        if "Error" in line or "Exception" in line:
                            error_type = line.strip()[:60]
                            break
                    error_details[error_type] += 1
                else:
                    error_details["Other Error"] += 1
            else:
                # Still running or incomplete
                running.append(log_file.name)
        
        except Exception as e:
            print(f"⚠️  Could not read {log_file.name}: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("SIMULATION STATUS SUMMARY")
    print("="*60)
    
    total = len(log_files)
    print(f"\nTotal log files: {total}")
    print(f"{'─'*60}")
    
    # Completed
    print(f"\n✓ COMPLETED: {len(completed)}/{total}")
    if completed and len(completed) <= 10:
        for name in completed[:5]:
            print(f"    {name}")
        if len(completed) > 5:
            print(f"    ... and {len(completed)-5} more")
    
    # Failed
    print(f"\n✗ FAILED/CRASHED: {len(failed)}/{total}")
    if failed and len(failed) <= 10:
        for name in failed[:5]:
            print(f"    {name}")
        if len(failed) > 5:
            print(f"    ... and {len(failed)-5} more")
    
    if error_details:
        print(f"\n  Error breakdown:")
        for error_type, count in sorted(error_details.items(), key=lambda x: -x[1]):
            print(f"    - {error_type}: {count}")
    
    # Running
    print(f"\n⏳ RUNNING/INCOMPLETE: {len(running)}/{total}")
    if running and len(running) <= 10:
        for name in running[:5]:
            print(f"    {name}")
        if len(running) > 5:
            print(f"    ... and {len(running)-5} more")
    
    # Summary line
    print(f"\n{'─'*60}")
    pct_complete = (len(completed) / total * 100) if total > 0 else 0
    pct_failed = (len(failed) / total * 100) if total > 0 else 0
    pct_running = (len(running) / total * 100) if total > 0 else 0
    
    print(f"Progress: {pct_complete:.1f}% complete, {pct_failed:.1f}% failed, {pct_running:.1f}% running")
    print("="*60 + "\n")


if __name__ == "__main__":
    analyze_logs()
