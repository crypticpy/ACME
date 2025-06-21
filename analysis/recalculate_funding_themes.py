#!/usr/bin/env python3
"""Recalculate cultural funding themes as percentage of unique respondents."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analyze_funding_themes():
    """Analyze funding-specific themes by unique respondents."""
    
    print("Loading survey data...")
    survey_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx")
    df = pd.read_excel(survey_path)
    
    print(f"Total respondents: {len(df)}")
    
    # Define funding-specific themes and their keywords
    funding_themes = {
        'Increase Funding Awareness': {
            'keywords': ['aware', 'awareness', 'know about', 'information', 'outreach', 
                        'communication', 'marketing', 'publicize', 'promote'],
            'description': 'Better information about funding opportunities'
        },
        'Support Small Organizations': {
            'keywords': ['small organization', 'emerging', 'grassroots', 'startup', 
                        'new organization', 'small nonprofit', 'small arts'],
            'description': 'Targeted support for smaller organizations'
        },
        'Simplify Application Process': {
            'keywords': ['application', 'apply', 'paperwork', 'process', 'bureaucracy', 
                        'red tape', 'complex', 'difficult', 'confusing', 'simplify'],
            'description': 'Streamline the application process'
        },
        'Improve Grant Access': {
            'keywords': ['grant access', 'eligibility', 'qualify', 'requirements', 
                        'restrictions', 'barriers to funding', 'consecutive years'],
            'description': 'Broaden access to grants'
        },
        'Funding Transparency': {
            'keywords': ['transparent', 'transparency', 'clear criteria', 'understand',
                        'clarity', 'open', 'decision', 'why', 'feedback'],
            'description': 'Clear funding decisions and criteria'
        },
        'Equitable Distribution': {
            'keywords': ['equitable', 'equity', 'fair', 'equal', 'inclusive', 
                        'diverse', 'underrepresented', 'marginalized'],
            'description': 'Fair distribution across communities'
        },
        'Increase Funding Levels': {
            'keywords': ['increase fund', 'more fund', 'additional fund', 'raise fund',
                        'expand fund', 'funding increase', 'not enough', 'insufficient'],
            'description': 'Increase available funding amounts'
        },
        'Multi-Year Funding': {
            'keywords': ['multi-year', 'multiyear', 'sustainable', 'long-term', 
                        'ongoing', 'recurring', 'stability'],
            'description': 'Provide multi-year commitments'
        },
        'Fair Artist Compensation': {
            'keywords': ['artist pay', 'fair pay', 'compensation', 'living wage', 
                        'payment', 'stipend', 'fee', 'remuneration'],
            'description': 'Ensure fair artist compensation'
        },
        'Reduce Reporting Burden': {
            'keywords': ['reporting', 'documentation', 'report requirement', 
                        'administrative burden', 'paperwork', 'metrics'],
            'description': 'Streamline reporting requirements'
        }
    }
    
    # Track unique respondents per theme
    theme_respondents = {theme: set() for theme in funding_themes}
    
    # Columns likely to contain funding feedback
    funding_columns = [
        'What improvements would you like to see in these cultural funding programs?',
        "Austin's creative community has built a strong foundation of existing organizations that informs ACME's goals and mission. How do you believe ACME should better support these organizations and cul...",
        'What barriers do you or your community face in accessing support or services related to arts, culture, music, and entertainment? ',
        'Do you have any additional ideas, concerns, or feedback you would like to share to help ACME better serve the public? ',
        'What kinds of programs or services would you like ACME to offer that currently do not exist or are underrepresented? '
    ]
    
    # Analyze each respondent's responses
    for idx, row in df.iterrows():
        # Check each funding-related column
        for col in funding_columns:
            if col in df.columns and pd.notna(row[col]):
                response = str(row[col]).lower()
                
                # Check for each theme's keywords
                for theme, theme_data in funding_themes.items():
                    for keyword in theme_data['keywords']:
                        if keyword.lower() in response:
                            theme_respondents[theme].add(idx)
                            break  # Count respondent only once per theme
    
    # Calculate results
    results = {
        'analysis_date': datetime.now().isoformat(),
        'total_respondents': len(df),
        'funding_themes': {}
    }
    
    # Sort themes by number of respondents
    sorted_themes = sorted(theme_respondents.items(), 
                          key=lambda x: len(x[1]), reverse=True)
    
    print("\n=== FUNDING THEME ANALYSIS (by unique respondents) ===")
    for rank, (theme, respondent_set) in enumerate(sorted_themes, 1):
        count = len(respondent_set)
        percentage = (count / len(df)) * 100
        
        results['funding_themes'][theme] = {
            'rank': rank,
            'count': count,
            'percentage': round(percentage, 1),
            'description': funding_themes[theme]['description']
        }
        
        print(f"{rank}. {theme}: {count} respondents ({percentage:.1f}%)")
    
    # Save results
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "funding_themes_by_respondent.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create comparison report
    print("\n=== COMPARISON WITH ORIGINAL ANALYSIS ===")
    
    # Load original analysis
    original_path = Path("data/results/cultural_funding_analysis/cultural_funding_themes.json")
    if original_path.exists():
        with open(original_path) as f:
            original = json.load(f)
        
        print("\nTheme | Original (mentions) | New (% respondents)")
        print("-" * 60)
        
        for theme_data in original['top_10_cultural_funding_themes']:
            theme = theme_data['theme']
            original_pct = theme_data['percentage']
            
            if theme in results['funding_themes']:
                new_pct = results['funding_themes'][theme]['percentage']
                print(f"{theme:<30} | {original_pct:>6.1f}% | {new_pct:>6.1f}%")
    
    print(f"\n✓ Analysis complete! Results saved to: {output_dir}/funding_themes_by_respondent.json")
    
    return results

if __name__ == "__main__":
    analyze_funding_themes()