#!/usr/bin/env python3
"""Live monitoring of deep analysis progress."""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def get_process_status():
    """Check if the analysis is still running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'run_deep_analysis.py'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def monitor_live():
    """Monitor the analysis with live updates."""
    
    question_response_counts = {
        "q1_org_support": 862,
        "q2_opportunities": 746,
        "q3_improvements": 595,
        "q4_barriers": 596,
        "q5_new_programs": 620,
        "q6_feedback": 859
    }
    total_expected = sum(question_response_counts.values())
    
    print("\033[2J\033[H")  # Clear screen
    print("🔍 ACME Deep Analysis Live Monitor")
    print("=" * 70)
    
    last_total = 0
    no_progress_count = 0
    
    while True:
        # Check process status
        is_running = get_process_status()
        
        # Count cached responses
        features_dir = Path("data/features/responses")
        total_cached = 0
        question_progress = {}
        
        for q_id, expected in question_response_counts.items():
            q_dir = features_dir / q_id
            if q_dir.exists():
                count = len(list(q_dir.glob("*.json")))
                total_cached += count
                question_progress[q_id] = (count, expected)
        
        # Clear and update display
        print("\033[2J\033[H")  # Clear screen
        print("🔍 ACME Deep Analysis Live Monitor")
        print("=" * 70)
        print(f"Status: {'🟢 Running' if is_running else '🔴 Stopped'}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Progress: {total_cached}/{total_expected} ({total_cached/total_expected*100:.1f}%)")
        print("-" * 70)
        
        # Progress bars
        for q_id, (cached, expected) in question_progress.items():
            percent = (cached / expected * 100) if expected > 0 else 0
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            status = "✅" if cached >= expected * 0.95 else "🔄" if cached > 0 else "⏳"
            print(f"{status} {q_id:<18} [{bar}] {cached:>4}/{expected:<4} ({percent:>5.1f}%)")
        
        # Check for stalls
        if total_cached == last_total:
            no_progress_count += 1
            if no_progress_count > 12:  # No progress for 2 minutes
                print("\n⚠️  Warning: No progress detected for 2 minutes")
        else:
            no_progress_count = 0
            
        last_total = total_cached
        
        # Check for completion
        if total_cached >= total_expected * 0.95:
            print("\n✅ Feature extraction nearly complete!")
            
        # Check for results
        results_dir = Path("data/results/deep_analysis")
        if results_dir.exists():
            results = list(results_dir.glob("deep_analysis_results_*.json"))
            if results:
                print(f"\n🎉 Analysis complete! Results saved to:")
                for r in results:
                    print(f"   {r}")
                break
        
        # Check logs for errors
        if Path("deep_analysis_continued.log").exists():
            try:
                result = subprocess.run(['tail', '-5', 'deep_analysis_continued.log'], 
                                      capture_output=True, text=True)
                if 'Error' in result.stdout or 'Fatal' in result.stdout:
                    print("\n❌ Error detected in log:")
                    print(result.stdout)
            except:
                pass
        
        if not is_running and total_cached < total_expected * 0.95:
            print("\n⚠️  Process stopped unexpectedly. Check logs for errors.")
            break
            
        time.sleep(10)  # Update every 10 seconds

if __name__ == "__main__":
    try:
        monitor_live()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")