#!/usr/bin/env python3
"""Analyze top 3 themes per cultural program."""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import pandas as pd

# Target programs as specified in NEW_ASK.md
TARGET_PROGRAMS = [
    "Nexus",
    "Thrive", 
    "Elevate",
    "Austin Live Music Fund",
    "Art in Public Places",
    "Creative Space Assistance Program"
]

def load_working_document_by_program():
    """Load and categorize recommendations by program."""
    working_doc_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Working_Document.xlsx")
    df = pd.read_excel(working_doc_path, sheet_name='Database')
    
    print(f"Loaded {len(df)} recommendations from working document")
    print(f"Columns: {list(df.columns)}")
    
    # Group by program
    program_data = defaultdict(list)
    
    if 'Program' in df.columns and 'Recommendation' in df.columns:
        for _, row in df.iterrows():
            program = str(row['Program'])
            recommendation = str(row['Recommendation'])
            
            if pd.notna(program) and pd.notna(recommendation):
                # Normalize program names
                program_normalized = program.strip()
                
                # Map variations to standard names
                if 'AIPP' in program or 'Art in Public' in program:
                    program_normalized = 'Art in Public Places'
                elif 'Music Fund' in program or 'Live Music' in program:
                    program_normalized = 'Austin Live Music Fund'
                elif 'Creative Space' in program:
                    program_normalized = 'Creative Space Assistance Program'
                
                program_data[program_normalized].append(recommendation)
    
    return program_data

def analyze_themes_for_program(recommendations, program_name):
    """Extract top 3 themes for a specific program."""
    
    # Theme keywords for cultural funding
    theme_keywords = {
        'Increase Funding': ['increase', 'expand', 'more fund', 'additional', 'raise', 'boost'],
        'Simplify Process': ['simplif', 'streamline', 'easier', 'reduce barrier', 'accessible', 'user-friendly'],
        'Equity & Access': ['equit', 'inclusive', 'divers', 'access', 'underserved', 'marginalized'],
        'Artist Support': ['artist', 'creative', 'individual', 'practitioner', 'performer', 'musician'],
        'Small Org Support': ['small', 'emerging', 'grassroot', 'startup', 'new org'],
        'Multi-Year Funding': ['multi-year', 'sustain', 'long-term', 'ongoing', 'recurring'],
        'Transparency': ['transparen', 'clear', 'understand', 'communicate', 'information'],
        'Community Engagement': ['community', 'engage', 'outreach', 'connect', 'participate'],
        'Infrastructure': ['space', 'venue', 'facility', 'equipment', 'resource'],
        'Collaboration': ['collaborat', 'partner', 'network', 'collective', 'together']
    }
    
    theme_counts = Counter()
    theme_examples = defaultdict(list)
    
    for rec in recommendations:
        rec_lower = rec.lower()
        
        # Check each theme
        for theme, keywords in theme_keywords.items():
            if any(keyword in rec_lower for keyword in keywords):
                theme_counts[theme] += 1
                if len(theme_examples[theme]) < 3:  # Collect up to 3 examples
                    theme_examples[theme].append(rec[:200])  # First 200 chars
    
    # Get top 3 themes
    top_themes = []
    for theme, count in theme_counts.most_common(3):
        top_themes.append({
            'theme': theme,
            'count': count,
            'percentage': round((count / len(recommendations)) * 100, 1) if recommendations else 0,
            'examples': theme_examples[theme]
        })
    
    return top_themes

def analyze_survey_for_programs():
    """Check survey data for program-specific mentions."""
    survey_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx")
    df = pd.read_excel(survey_path)
    
    program_mentions = defaultdict(list)
    
    # Search all text columns for program mentions
    text_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    for col in text_columns:
        for response in df[col].dropna():
            response_str = str(response)
            response_lower = response_str.lower()
            
            # Check for each program
            for program in TARGET_PROGRAMS:
                program_lower = program.lower()
                
                # Various ways programs might be mentioned
                if program_lower in response_lower:
                    program_mentions[program].append({
                        'column': col,
                        'response': response_str[:300]
                    })
                elif program == "Art in Public Places" and ('aipp' in response_lower or 'public art' in response_lower):
                    program_mentions[program].append({
                        'column': col,
                        'response': response_str[:300]
                    })
                elif program == "Austin Live Music Fund" and ('music fund' in response_lower or 'live music' in response_lower):
                    program_mentions[program].append({
                        'column': col,
                        'response': response_str[:300]
                    })
    
    return program_mentions

def generate_program_analysis():
    """Generate complete program-specific theme analysis."""
    
    print("=== PROGRAM-SPECIFIC THEME ANALYSIS ===\n")
    
    # Load data
    print("1. Loading working document recommendations by program...")
    program_recommendations = load_working_document_by_program()
    
    print("\n2. Analyzing survey data for program mentions...")
    survey_program_mentions = analyze_survey_for_programs()
    
    # Analyze each target program
    results = {
        "analysis_date": datetime.now().isoformat(),
        "programs_analyzed": []
    }
    
    output_md = """# Top 3 Themes per Program

**Generated:** """ + datetime.now().strftime('%B %d, %Y') + "\n\n"
    
    for program in TARGET_PROGRAMS:
        print(f"\n=== {program.upper()} ===")
        
        # Get recommendations for this program
        recommendations = program_recommendations.get(program, [])
        print(f"Found {len(recommendations)} recommendations")
        
        # Get survey mentions
        survey_mentions = survey_program_mentions.get(program, [])
        print(f"Found {len(survey_mentions)} survey mentions")
        
        # Analyze themes
        if recommendations:
            top_themes = analyze_themes_for_program(recommendations, program)
        else:
            # If no direct recommendations, analyze survey mentions
            survey_texts = [m['response'] for m in survey_mentions]
            top_themes = analyze_themes_for_program(survey_texts, program) if survey_texts else []
        
        # Add to results
        program_result = {
            "program": program,
            "recommendation_count": len(recommendations),
            "survey_mention_count": len(survey_mentions),
            "top_3_themes": []
        }
        
        output_md += f"## {program}\n\n"
        
        if top_themes:
            for i, theme_info in enumerate(top_themes, 1):
                print(f"\n{i}. {theme_info['theme']}")
                print(f"   Count: {theme_info['count']} ({theme_info['percentage']}%)")
                
                program_result["top_3_themes"].append({
                    "rank": i,
                    "theme": theme_info['theme'],
                    "count": theme_info['count'],
                    "percentage": theme_info['percentage']
                })
                
                output_md += f"**{i}. {theme_info['theme']}** ({theme_info['count']} mentions, {theme_info['percentage']}%)\n"
                
                if theme_info['examples']:
                    print("   Examples:")
                    for j, example in enumerate(theme_info['examples'][:2], 1):
                        print(f"   - {example[:100]}...")
                        output_md += f"   - {example}\n"
                
                output_md += "\n"
        else:
            print("   No specific themes identified")
            output_md += "*No specific recommendation data available for this program*\n\n"
        
        results["programs_analyzed"].append(program_result)
    
    # Save results
    output_dir = Path("data/results/cultural_funding_analysis")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with open(output_dir / "program_themes_analysis.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    with open(output_dir / "PROGRAM_THEMES_ANALYSIS.md", 'w') as f:
        f.write(output_md)
    
    print(f"\n✓ Program analysis complete! Results saved to: {output_dir}")
    print("  - program_themes_analysis.json")
    print("  - PROGRAM_THEMES_ANALYSIS.md")

if __name__ == "__main__":
    generate_program_analysis()