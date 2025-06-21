#!/usr/bin/env python3
"""Check the progress of the deep analysis."""

import json
from pathlib import Path
from datetime import datetime

def check_progress():
    """Check analysis progress by examining cache files."""
    
    # Check feature extraction cache
    features_dir = Path("data/features/responses")
    if features_dir.exists():
        question_dirs = list(features_dir.glob("q*"))
        print(f"Questions being analyzed: {len(question_dirs)}")
        
        total_cached = 0
        for q_dir in question_dirs:
            cache_files = list(q_dir.glob("*.json"))
            print(f"\n{q_dir.name}: {len(cache_files)} responses cached")
            total_cached += len(cache_files)
        
        print(f"\nTotal responses cached: {total_cached}")
    
    # Check for question analysis results
    questions_dir = Path("data/features/questions")
    if questions_dir.exists():
        analysis_files = list(questions_dir.glob("*.json"))
        print(f"\nCompleted question analyses: {len(analysis_files)}")
        for f in analysis_files:
            print(f"  - {f.name}")
    
    # Check for final results
    results_dir = Path("data/results/deep_analysis")
    if results_dir.exists():
        result_files = list(results_dir.glob("deep_analysis_results_*.json"))
        if result_files:
            print(f"\nCompleted analysis files: {len(result_files)}")
            latest = sorted(result_files)[-1]
            print(f"Latest: {latest.name}")
            
            # Show summary of latest results
            with open(latest, 'r') as f:
                data = json.load(f)
                meta = data.get('metadata', {})
                print(f"\nAnalysis Summary:")
                print(f"  Total responses: {meta.get('total_responses', 'N/A')}")
                print(f"  Questions analyzed: {meta.get('questions_analyzed', 'N/A')}")
                print(f"  Programs analyzed: {meta.get('programs_analyzed', 'N/A')}")
                print(f"  Duration: {meta.get('analysis_duration', 'N/A')}")
    
    # Check audit logs
    audit_dir = Path("data/audit")
    if audit_dir.exists():
        log_files = sorted(audit_dir.glob("operations_*.jsonl"))
        if log_files:
            latest_log = log_files[-1]
            print(f"\nLatest audit log: {latest_log.name}")
            
            # Count recent operations
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                recent_ops = []
                for line in lines[-10:]:  # Last 10 operations
                    try:
                        op = json.loads(line)
                        recent_ops.append(f"  {op['timestamp']}: {op['operation']}")
                    except:
                        pass
                
                if recent_ops:
                    print("\nRecent operations:")
                    for op in recent_ops:
                        print(op)

if __name__ == "__main__":
    check_progress()