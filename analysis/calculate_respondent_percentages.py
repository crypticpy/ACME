#!/usr/bin/env python3
"""
Calculate percentage of unique respondents who mentioned each cultural funding theme.
This script analyzes the ACME Community Survey data to provide accurate respondent counts.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import re
from datetime import datetime

# Define the cultural funding themes to search for
FUNDING_THEMES = {
    'public_art': ['public art', 'murals', 'sculptures', 'installations', 'street art'],
    'arts_education': ['arts education', 'art education', 'teaching', 'workshops', 'classes', 'youth programs'],
    'cultural_events': ['cultural events', 'festivals', 'performances', 'concerts', 'exhibitions'],
    'community_spaces': ['community spaces', 'art spaces', 'galleries', 'studios', 'creative spaces'],
    'artist_support': ['artist support', 'grants', 'residencies', 'stipends', 'artist funding'],
    'cultural_preservation': ['cultural preservation', 'heritage', 'traditions', 'history', 'archives'],
    'digital_arts': ['digital arts', 'digital art', 'technology', 'multimedia', 'virtual', 'online'],
    'accessibility': ['accessibility', 'accessible', 'inclusive', 'disability', 'adaptive']
}

def load_survey_data(file_path):
    """Load the survey data from Excel file."""
    print(f"Loading survey data from: {file_path}")
    try:
        # Read all sheets to understand structure
        xl_file = pd.ExcelFile(file_path)
        print(f"Found sheets: {xl_file.sheet_names}")
        
        # Load the main data sheet (usually the first one)
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"Loaded {len(df)} responses")
        print(f"Columns: {list(df.columns)}")
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def identify_text_columns(df):
    """Identify columns that likely contain text responses about cultural funding."""
    text_columns = []
    
    # Look for columns that might contain relevant responses
    keywords = ['cultural', 'funding', 'art', 'community', 'priority', 'importance', 
                'support', 'need', 'want', 'improve', 'suggest', 'comment', 'response',
                'q', 'question', 'what', 'how', 'why']
    
    for col in df.columns:
        col_lower = str(col).lower()
        # Check if column name contains relevant keywords
        if any(keyword in col_lower for keyword in keywords):
            # Also check if it contains text data
            if df[col].dtype == 'object':
                non_null_count = df[col].notna().sum()
                if non_null_count > 0:
                    text_columns.append(col)
                    print(f"Found text column: {col} (responses: {non_null_count})")
    
    return text_columns

def search_theme_in_text(text, theme_keywords):
    """Search for theme keywords in text, case-insensitive."""
    if pd.isna(text):
        return False
    
    text_lower = str(text).lower()
    return any(keyword in text_lower for keyword in theme_keywords)

def calculate_theme_percentages(df, text_columns):
    """Calculate percentage of respondents mentioning each theme."""
    results = {}
    total_respondents = len(df)
    
    print(f"\nAnalyzing {total_respondents} total respondents...")
    
    for theme_name, keywords in FUNDING_THEMES.items():
        # Track unique respondents who mentioned this theme
        respondent_mentioned = np.zeros(len(df), dtype=bool)
        
        # Check each text column for theme mentions
        for col in text_columns:
            for idx, response in enumerate(df[col]):
                if search_theme_in_text(response, keywords):
                    respondent_mentioned[idx] = True
        
        # Calculate statistics
        count = respondent_mentioned.sum()
        percentage = (count / total_respondents) * 100 if total_respondents > 0 else 0
        
        results[theme_name] = {
            'count': int(count),
            'percentage': round(percentage, 2),
            'theme_display_name': theme_name.replace('_', ' ').title()
        }
        
        print(f"{theme_name}: {count} respondents ({percentage:.1f}%)")
    
    return results

def analyze_geographic_distribution(df, theme_results):
    """Analyze geographic distribution if ZIP code data is available."""
    geo_results = {}
    
    # Look for ZIP code column
    zip_columns = [col for col in df.columns if 'zip' in str(col).lower() or 'postal' in str(col).lower()]
    
    if zip_columns:
        zip_col = zip_columns[0]
        print(f"\nFound ZIP code column: {zip_col}")
        
        # Clean ZIP codes
        df['clean_zip'] = df[zip_col].astype(str).str[:5].str.strip()
        valid_zips = df[df['clean_zip'].str.match(r'^\d{5}$', na=False)]
        
        print(f"Valid ZIP codes: {len(valid_zips)} out of {len(df)}")
        
        # Count respondents by ZIP
        zip_counts = valid_zips['clean_zip'].value_counts()
        geo_results['zip_distribution'] = {
            'total_zips': len(zip_counts),
            'top_zips': zip_counts.head(10).to_dict(),
            'coverage': round((len(valid_zips) / len(df)) * 100, 2)
        }
    
    return geo_results

def save_results(results, geo_results, output_dir):
    """Save analysis results in multiple formats."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Combine all results
    full_results = {
        'analysis_date': datetime.now().isoformat(),
        'total_respondents': results.get('total_respondents', 0),
        'themes': results.get('themes', {}),
        'geographic': geo_results,
        'methodology': {
            'description': 'Each respondent counted only once per theme',
            'themes_analyzed': list(FUNDING_THEMES.keys()),
            'text_columns_analyzed': results.get('columns_analyzed', [])
        }
    }
    
    # Save as JSON
    json_path = output_dir / 'respondent_theme_analysis.json'
    with open(json_path, 'w') as f:
        json.dump(full_results, f, indent=2)
    print(f"\nSaved JSON results to: {json_path}")
    
    # Save summary CSV
    csv_data = []
    for theme_name, theme_data in results.get('themes', {}).items():
        csv_data.append({
            'Theme': theme_data['theme_display_name'],
            'Respondent Count': theme_data['count'],
            'Percentage': f"{theme_data['percentage']}%",
            'Keywords Used': ', '.join(FUNDING_THEMES.get(theme_name, [])[:3]) + '...'
        })
    
    csv_df = pd.DataFrame(csv_data)
    csv_df = csv_df.sort_values('Respondent Count', ascending=False)
    csv_path = output_dir / 'theme_percentages_summary.csv'
    csv_df.to_csv(csv_path, index=False)
    print(f"Saved CSV summary to: {csv_path}")
    
    # Create markdown report
    create_markdown_report(full_results, output_dir)

def create_markdown_report(results, output_dir):
    """Create a markdown report of the analysis."""
    md_path = output_dir / 'analysis_report.md'
    
    with open(md_path, 'w') as f:
        f.write("# ACME Cultural Funding Survey Analysis\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- Total Respondents: {results.get('total_respondents', 0)}\n")
        f.write(f"- Themes Analyzed: {len(results.get('themes', {}))}\n")
        f.write(f"- Text Columns Analyzed: {len(results.get('methodology', {}).get('text_columns_analyzed', []))}\n\n")
        
        f.write("## Theme Analysis Results\n\n")
        f.write("| Theme | Respondents | Percentage |\n")
        f.write("|-------|-------------|------------|\n")
        
        # Sort themes by count
        sorted_themes = sorted(
            results.get('themes', {}).items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        for theme_name, theme_data in sorted_themes:
            f.write(f"| {theme_data['theme_display_name']} | {theme_data['count']} | {theme_data['percentage']}% |\n")
        
        # Add geographic insights if available
        if results.get('geographic', {}).get('zip_distribution'):
            f.write("\n## Geographic Distribution\n\n")
            geo = results['geographic']['zip_distribution']
            f.write(f"- ZIP codes with responses: {geo['total_zips']}\n")
            f.write(f"- Geographic coverage: {geo['coverage']}% of respondents provided valid ZIP codes\n\n")
            
            f.write("### Top 10 ZIP Codes by Response Count\n\n")
            f.write("| ZIP Code | Responses |\n")
            f.write("|----------|----------|\n")
            for zip_code, count in geo['top_zips'].items():
                f.write(f"| {zip_code} | {count} |\n")
    
    print(f"Saved markdown report to: {md_path}")

def main():
    """Main analysis function."""
    # File paths
    survey_file = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx")
    output_dir = Path("/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/analysis/results")
    
    # Load data
    df = load_survey_data(survey_file)
    if df is None:
        return
    
    # Identify text columns
    text_columns = identify_text_columns(df)
    if not text_columns:
        print("Warning: No text columns found. Checking all object columns...")
        text_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    # Calculate theme percentages
    theme_results = calculate_theme_percentages(df, text_columns)
    
    # Analyze geographic distribution
    geo_results = analyze_geographic_distribution(df, theme_results)
    
    # Prepare final results
    final_results = {
        'total_respondents': len(df),
        'themes': theme_results,
        'columns_analyzed': text_columns
    }
    
    # Save results
    save_results(final_results, geo_results, output_dir)
    
    print("\n✓ Analysis complete!")
    print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    main()