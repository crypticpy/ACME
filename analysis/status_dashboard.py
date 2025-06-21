#!/usr/bin/env python3
"""Simple status dashboard for deep analysis."""

from pathlib import Path
from datetime import datetime
import subprocess

def show_status():
    """Display current analysis status."""
    
    questions = {
        "q1_org_support": ("How do you believe ACME should better support?", 862),
        "q2_opportunities": ("What opportunities would you like to see?", 746),
        "q3_improvements": ("What improvements in funding programs?", 595),
        "q4_barriers": ("What barriers do you face?", 596),
        "q5_new_programs": ("What new programs should ACME offer?", 620),
        "q6_feedback": ("Any additional feedback?", 859)
    }
    
    print("\n" + "="*80)
    print(f"ACME Deep Analysis Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check if running
    try:
        result = subprocess.run(['pgrep', '-f', 'run_deep_analysis.py'], 
                              capture_output=True, text=True)
        is_running = len(result.stdout.strip()) > 0
        print(f"Process Status: {'🟢 RUNNING' if is_running else '🔴 STOPPED'}")
    except:
        print("Process Status: Unknown")
    
    print("\nQuestion Progress:")
    print("-"*80)
    
    total_expected = sum(q[1] for q in questions.values())
    total_cached = 0
    
    features_dir = Path("data/features/responses")
    
    for q_id, (desc, expected) in questions.items():
        q_dir = features_dir / q_id
        if q_dir.exists():
            cached = len(list(q_dir.glob("*.json")))
            total_cached += cached
            percent = (cached / expected * 100) if expected > 0 else 0
            
            # Status icon
            if cached >= expected * 0.95:
                status = "✅"
            elif cached > 0:
                status = "🔄"
            else:
                status = "⏳"
            
            # Progress bar
            bar_width = 30
            filled = int(bar_width * percent / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            print(f"{status} {q_id:<20} [{bar}] {cached:>4}/{expected:<4} ({percent:>5.1f}%)")
            print(f"   {desc[:50]}")
        else:
            print(f"⏳ {q_id:<20} [{'░' * 30}]    0/{expected:<4} (  0.0%)")
            print(f"   {desc[:50]}")
        print()
    
    print("-"*80)
    print(f"Total Progress: {total_cached}/{total_expected} ({total_cached/total_expected*100:.1f}%)")
    
    # Check for completed analyses
    questions_dir = Path("data/features/questions")
    if questions_dir.exists():
        completed = len(list(questions_dir.glob("*.json")))
        print(f"Completed Question Analyses: {completed}")
    
    # Check for final results
    results_dir = Path("data/results/deep_analysis")
    if results_dir.exists():
        results = list(results_dir.glob("deep_analysis_results_*.json"))
        if results:
            print(f"\n✅ ANALYSIS COMPLETE!")
            print(f"Results saved to: {results[0]}")

if __name__ == "__main__":
    show_status()