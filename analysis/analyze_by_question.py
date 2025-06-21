#!/usr/bin/env python3
"""Analyze survey responses question by question."""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table

console = Console()

def analyze_questions_individually():
    """Analyze each survey question separately to maintain context."""
    
    # Load survey data
    survey_path = Path("data/raw/ACME_Community_Survey.xlsx")
    df = pd.read_excel(survey_path)
    
    console.print(f"[blue]Loaded {len(df)} survey responses[/]")
    
    # Find all text response columns
    text_columns = []
    for col in df.columns:
        non_null = df[col].dropna()
        if len(non_null) > 50:  # At least 50 responses
            # Check if it's text data
            sample = non_null.head(10)
            if sample.dtype == 'object' and sample.str.len().mean() > 30:
                text_columns.append(col)
    
    console.print(f"\n[yellow]Found {len(text_columns)} text response questions:[/]")
    
    # Create analysis summary
    question_analysis = {}
    
    for i, col in enumerate(text_columns, 1):
        responses = df[col].dropna()
        text_responses = responses[responses.str.len() > 20]
        
        if len(text_responses) < 10:
            continue
            
        console.print(f"\n[bold]{i}. {col}[/]")
        console.print(f"   Responses: {len(text_responses)}")
        
        # Analyze response patterns
        question_analysis[col] = {
            "question": col,
            "total_responses": len(text_responses),
            "sample_responses": text_responses.head(5).tolist(),
            "avg_length": int(text_responses.str.len().mean()),
            "common_words": find_common_themes(text_responses)
        }
        
        # Display sample
        table = Table(title=f"Sample Responses", show_header=False)
        table.add_column("Response", style="dim")
        
        for resp in text_responses.head(3):
            table.add_row(resp[:150] + "..." if len(resp) > 150 else resp)
        
        console.print(table)
    
    # Save detailed analysis
    output_path = Path("data/results/question_by_question_analysis.json")
    with open(output_path, 'w') as f:
        json.dump(question_analysis, f, indent=2)
    
    console.print(f"\n[green]✓ Saved detailed analysis to {output_path}[/]")
    
    return question_analysis

def find_common_themes(responses):
    """Extract common themes from responses using simple word frequency."""
    from collections import Counter
    import re
    
    # Common words to ignore
    stop_words = {'the', 'and', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'with', 'as', 'at', 'by', 'an', 'be', 'this', 'that', 'it', 'from', 'or', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'i', 'you', 'we', 'they', 'he', 'she', 'me', 'my', 'your', 'our', 'their', 'what', 'when', 'where', 'who', 'why', 'how', 'all', 'more', 'less', 'very', 'so', 'too', 'also', 'just', 'but', 'if', 'than', 'then', 'there', 'these', 'those', 'some', 'any', 'no', 'not', 'yes'}
    
    # Extract words from all responses
    all_words = []
    for resp in responses:
        words = re.findall(r'\b\w+\b', str(resp).lower())
        all_words.extend([w for w in words if len(w) > 3 and w not in stop_words])
    
    # Get top themes
    word_counts = Counter(all_words)
    top_themes = word_counts.most_common(10)
    
    return [{"word": word, "count": count} for word, count in top_themes]

if __name__ == "__main__":
    analyze_questions_individually()