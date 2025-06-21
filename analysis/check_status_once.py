#!/usr/bin/env python3
"""Check analysis status once."""

import json
from pathlib import Path
from datetime import datetime, timedelta

# Define expected totals
question_response_counts = {
    "q1_org_support": 862,
    "q2_opportunities": 746,
    "q3_improvements": 595,
    "q4_barriers": 596,
    "q5_new_programs": 620, 
    "q6_feedback": 859
}
total_expected = sum(question_response_counts.values())

print("ACME Deep Analysis Progress")
print("=" * 60)

# Count cached responses
features_dir = Path("data/features/responses")
total_cached = 0
question_progress = {}

if features_dir.exists():
    for q_id, expected_count in question_response_counts.items():
        q_dir = features_dir / q_id
        if q_dir.exists():
            cache_files = list(q_dir.glob("*.json"))
            count = len(cache_files)
            total_cached += count
            question_progress[q_id] = {
                "cached": count,
                "expected": expected_count,
                "percent": (count / expected_count * 100) if expected_count > 0 else 0
            }

# Display progress
print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total Progress: {total_cached}/{total_expected} ({total_cached/total_expected*100:.1f}%)")
print("-" * 60)

for q_id, progress in question_progress.items():
    bar_length = 30
    filled = int(bar_length * progress["percent"] / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"{q_id:<20} [{bar}] {progress['cached']:>4}/{progress['expected']:<4} ({progress['percent']:>5.1f}%)")

# Get timing info from first cache file
if total_cached > 0:
    first_file_time = None
    last_file_time = None
    
    for q_dir in features_dir.glob("q*"):
        for cache_file in q_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if first_file_time is None or mtime < first_file_time:
                first_file_time = mtime
            if last_file_time is None or mtime > last_file_time:
                last_file_time = mtime
    
    if first_file_time and last_file_time:
        duration = last_file_time - first_file_time
        if duration.total_seconds() > 0:
            rate = total_cached / duration.total_seconds()
            print(f"\nAnalysis started: {first_file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last update: {last_file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration so far: {duration}")
            print(f"Average rate: {rate:.3f} responses/second")
            
            if rate > 0:
                remaining = total_expected - total_cached
                eta_seconds = remaining / rate
                eta = timedelta(seconds=int(eta_seconds))
                print(f"\nEstimated time remaining: {eta}")
                print(f"Estimated completion: {(datetime.now() + eta).strftime('%Y-%m-%d %H:%M:%S')}")