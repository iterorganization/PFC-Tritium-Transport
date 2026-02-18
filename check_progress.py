#!/usr/bin/env python3
"""
Check progress of SLURM jobs from .err files.

Reads all .err files in logs folder and prints their current progress %.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def extract_progress_and_time(content):
    """Extract progress percentage, elapsed time, and sim/end times from the progress bar line."""
    lines = content.split('\n')
    progress = None
    elapsed_time = None
    sim_time = None
    end_time = None
    
    # Look for progress bar format: "14%|█▍        | 3.76M/26.7M [59:01<95:08:44, 67.1it/s]"
    # This pattern extracts: progress%, current/total, [elapsed<remaining, rate]
    # Using [KMGTkmgt]? to match both uppercase and lowercase suffixes
    progress_bar_pattern = r'(\d+)%\|.*?\|\s*([\d.]+[KMGTkmgt]?)\/([\d.]+[KMGTkmgt]?)\s+\[(\d+):(\d+)(?::(\d+))?'
    
    def parse_number(s):
        """Convert number with K/M/G/T suffix to float (case-insensitive)."""
        multipliers = {'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12}
        s = str(s).strip().upper()  # Convert to uppercase for case-insensitive matching
        for suffix, mult in multipliers.items():
            if suffix in s:
                return float(s.replace(suffix, '')) * mult
        return float(s)
    
    for line in reversed(lines):
        match = re.search(progress_bar_pattern, line)
        if match:
            progress = float(match.group(1))
            
            # Extract current and total values from progress bar
            current_val = parse_number(match.group(2))
            total_val = parse_number(match.group(3))
            
            # Skip if current is 0 (not enough progress to estimate)
            if current_val <= 0:
                continue
            
            sim_time = current_val
            end_time = total_val
            
            # Extract elapsed time [MM:SS] or [HH:MM:SS]
            first_part = int(match.group(4))
            second_part = int(match.group(5))
            third_part = int(match.group(6)) if match.group(6) else None
            
            # Determine if format is MM:SS or HH:MM:SS
            if third_part is not None:
                # Format is HH:MM:SS
                elapsed_time = first_part * 3600 + second_part * 60 + third_part
            else:
                # Format is MM:SS
                elapsed_time = first_part * 60 + second_part
            
            return progress, elapsed_time, sim_time, end_time
        
        # Fallback: Look for percentage patterns
        if progress is None:
            match = re.search(r'(\d+\.?\d*)\s*%', line)
            if match:
                progress = float(match.group(1))
        
        # Look for "bin X of Y" patterns
        if progress is None:
            match = re.search(r'bin\s+(\d+)\s+of\s+(\d+)', line, re.IGNORECASE)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                progress = (current / total) * 100
        
        # Look for iteration/step progress patterns
        if progress is None:
            match = re.search(r'step\s+(\d+)/(\d+)', line, re.IGNORECASE)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                progress = (current / total) * 100
    
    return progress, elapsed_time, sim_time, end_time


def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def estimate_remaining_time(elapsed_time, sim_time, end_time):
    """Calculate remaining time using: elapsed_time * (end_time / sim_time - 1)
    
    Returns None if there's not enough progress to estimate reliably.
    """
    if elapsed_time is None or sim_time is None or end_time is None or sim_time <= 0:
        return None
    
    # Don't estimate if we have almost no progress (less than 0.1% complete)
    if sim_time < 0.001 * end_time:
        return None
    
    # Formula: remaining = elapsed * (end_time / sim_time - 1)
    remaining = elapsed_time * (end_time / sim_time - 1)
    return max(0, remaining)


def analyze_err_files():
    """Analyze all .err files in logs folder and report progress."""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("❌ logs folder not found")
        return
    
    # Get all .err files, sorted by job ID
    err_files = sorted(logs_dir.glob("*.err"), key=lambda x: x.name)
    
    if not err_files:
        print("❌ No .err files found in logs folder")
        return
    
    progress_data = []
    
    # Analyze each .err file
    for err_file in err_files:
        try:
            with open(err_file, 'r', errors='ignore') as f:
                content = f.read()
            
            progress, elapsed_time, sim_time, end_time = extract_progress_and_time(content)
            remaining_time_est = estimate_remaining_time(elapsed_time, sim_time, end_time)
            job_name = err_file.stem  # e.g., "new_csv_bin_1_861152"
            
            progress_data.append({
                'name': job_name,
                'progress': progress,
                'elapsed': elapsed_time,
                'remaining': remaining_time_est,
                'file': err_file.name
            })
        
        except Exception as e:
            print(f"⚠️  Could not read {err_file.name}: {e}")
    
    # Sort by progress
    progress_data.sort(key=lambda x: x['progress'] if x['progress'] is not None else -1, reverse=True)
    
    # Print results
    print("\n" + "="*90)
    print("JOB PROGRESS SUMMARY")
    print("="*90)
    print(f"{'Job Name':<35} {'Progress':<12} {'Elapsed':<12} {'Remaining':<12}")
    print("-"*90)
    
    completed = 0
    in_progress = 0
    unknown = 0
    total_progress = 0.0
    
    for item in progress_data:
        if item['progress'] is not None:
            progress_pct = item['progress']
            total_progress += progress_pct
            
            if progress_pct >= 100:
                status = "✓ DONE"
                completed += 1
                elapsed_display = format_time(item['elapsed'])
                remaining_display = "00:00:00"
            else:
                status = f"{progress_pct:6.1f}%"
                in_progress += 1
                elapsed_display = format_time(item['elapsed'])
                remaining_display = format_time(item['remaining'])
            
            # Truncate long names
            job_display = item['name'][:33]
            print(f"{job_display:<35} {status:<12} {elapsed_display:<12} {remaining_display:<12}")
        else:
            unknown += 1
            print(f"{item['name'][:33]:<35} {'(no info)':<12} {'N/A':<12} {'N/A':<12}")
    
    # Summary
    print("-"*90)
    total = len(progress_data)
    avg_progress = ((total_progress - completed * 100) / in_progress) if in_progress > 0 else 0
    
    print(f"\nSummary:")
    print(f"  Total jobs: {total}")
    print(f"  Completed: {completed}")
    print(f"  In progress: {in_progress} (avg {avg_progress:.1f}%)")
    print(f"  Unknown progress: {unknown}")
    print("="*90 + "\n")


if __name__ == "__main__":
    analyze_err_files()
