#!/usr/bin/env python3
"""Monitor deep analysis progress with time estimates."""

import json
from pathlib import Path
from datetime import datetime, timedelta
import time

def monitor_progress():
    """Monitor analysis progress with estimates."""
    
    # Define expected totals from the data
    question_response_counts = {
        "q1_org_support": 862,
        "q2_opportunities": 746,
        "q3_improvements": 595,
        "q4_barriers": 596,
        "q5_new_programs": 620, 
        "q6_feedback": 859
    }
    total_expected = sum(question_response_counts.values())  # 4,278
    
    print("ACME Deep Analysis Progress Monitor")
    print("=" * 60)
    
    while True:
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
        
        # Estimate completion time
        if total_cached > 50:  # Need some data to estimate
            # Simple estimation based on current progress
            # Assume linear progress (not perfect but gives rough idea)
            remaining = total_expected - total_cached
            
            # Check how long we've been running by looking at oldest cache file
            oldest_time = None
            for q_dir in features_dir.glob("q*"):
                for cache_file in q_dir.glob("*.json"):
                    mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if oldest_time is None or mtime < oldest_time:
                        oldest_time = mtime
            
            if oldest_time:
                elapsed = datetime.now() - oldest_time
                if elapsed.total_seconds() > 0:
                    rate = total_cached / elapsed.total_seconds()  # responses per second
                    if rate > 0:
                        eta_seconds = remaining / rate
                        eta = timedelta(seconds=int(eta_seconds))
                        print(f"\nProcessing rate: {rate:.2f} responses/second")
                        print(f"Estimated time remaining: {eta}")
                        print(f"Estimated completion: {(datetime.now() + eta).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for completed analyses
        questions_dir = Path("data/features/questions")
        if questions_dir.exists():
            completed = list(questions_dir.glob("*.json"))
            if completed:
                print(f"\nCompleted question analyses: {len(completed)}")
        
        # Check for final results
        results_dir = Path("data/results/deep_analysis")
        if results_dir.exists():
            result_files = list(results_dir.glob("deep_analysis_results_*.json"))
            if result_files:
                print(f"\n✓ ANALYSIS COMPLETE! Results saved to:")
                for f in result_files:
                    print(f"  {f}")
                break
        
        print("\n" + "=" * 60)
        print("Press Ctrl+C to stop monitoring...")
        
        # Wait 30 seconds before next update
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_progress()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")