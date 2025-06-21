#!/usr/bin/env python3
"""
Create visualizations for the cultural funding theme analysis results.
Generates charts and data files ready for the microsite.
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_analysis_results():
    """Load the analysis results from JSON."""
    with open('results/respondent_theme_analysis.json', 'r') as f:
        return json.load(f)

def create_theme_bar_chart(data):
    """Create a horizontal bar chart of theme percentages."""
    # Extract theme data
    themes = []
    percentages = []
    counts = []
    
    for theme_key, theme_data in data['themes'].items():
        themes.append(theme_data['theme_display_name'])
        percentages.append(theme_data['percentage'])
        counts.append(theme_data['count'])
    
    # Create DataFrame for easier plotting
    df = pd.DataFrame({
        'Theme': themes,
        'Percentage': percentages,
        'Count': counts
    }).sort_values('Percentage', ascending=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create horizontal bar chart
    bars = ax.barh(df['Theme'], df['Percentage'], color='#4A90E2')
    
    # Add percentage labels
    for i, (percentage, count) in enumerate(zip(df['Percentage'], df['Count'])):
        ax.text(percentage + 1, i, f'{percentage}%', va='center', fontsize=10)
        ax.text(percentage/2, i, f'{count} respondents', va='center', ha='center', 
                color='white', fontsize=9, fontweight='bold')
    
    # Customize the chart
    ax.set_xlabel('Percentage of Respondents', fontsize=12)
    ax.set_ylabel('Cultural Funding Themes', fontsize=12)
    ax.set_title('ACME Community Survey: Cultural Funding Theme Mentions\n'
                 f'Based on {data["total_respondents"]} unique respondents', 
                 fontsize=14, pad=20)
    ax.set_xlim(0, 100)
    
    # Add grid
    ax.grid(axis='x', alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Save chart
    plt.savefig('results/theme_percentages_chart.png', dpi=300, bbox_inches='tight')
    plt.savefig('results/theme_percentages_chart.svg', format='svg', bbox_inches='tight')
    print("Saved theme percentage charts")
    
    plt.close()

def create_geographic_visualization(data):
    """Create visualization of geographic distribution."""
    if not data.get('geographic', {}).get('zip_distribution'):
        print("No geographic data available")
        return
    
    geo_data = data['geographic']['zip_distribution']
    top_zips = geo_data['top_zips']
    
    # Create DataFrame
    zip_codes = list(top_zips.keys())
    counts = list(top_zips.values())
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create bar chart
    bars = ax.bar(zip_codes, counts, color='#E94B3C')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # Customize
    ax.set_xlabel('ZIP Code', fontsize=12)
    ax.set_ylabel('Number of Respondents', fontsize=12)
    ax.set_title(f'Top 10 ZIP Codes by Survey Response Count\n'
                 f'Total: {geo_data["total_zips"]} ZIP codes represented', 
                 fontsize=14, pad=20)
    
    # Rotate x labels
    plt.xticks(rotation=45)
    
    # Add grid
    ax.grid(axis='y', alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig('results/geographic_distribution_chart.png', dpi=300, bbox_inches='tight')
    print("Saved geographic distribution chart")
    
    plt.close()

def prepare_microsite_data(data):
    """Prepare data in formats ready for the microsite."""
    # Create simplified JSON for web use
    web_data = {
        'survey_stats': {
            'total_respondents': data['total_respondents'],
            'analysis_date': data['analysis_date'],
            'zip_codes_represented': data['geographic']['zip_distribution']['total_zips']
        },
        'themes': []
    }
    
    # Sort themes by percentage
    sorted_themes = sorted(
        data['themes'].items(),
        key=lambda x: x[1]['percentage'],
        reverse=True
    )
    
    for theme_key, theme_data in sorted_themes:
        web_data['themes'].append({
            'id': theme_key,
            'name': theme_data['theme_display_name'],
            'percentage': theme_data['percentage'],
            'count': theme_data['count'],
            'description': get_theme_description(theme_key)
        })
    
    # Save web-ready JSON
    with open('results/microsite_data.json', 'w') as f:
        json.dump(web_data, f, indent=2)
    
    # Create JavaScript module
    js_content = f"// ACME Cultural Funding Theme Data\n"
    js_content += f"// Generated from survey analysis on {data['analysis_date']}\n\n"
    js_content += f"export const surveyData = {json.dumps(web_data, indent=2)};\n"
    
    with open('results/survey_data.js', 'w') as f:
        f.write(js_content)
    
    print("Created microsite data files")

def get_theme_description(theme_key):
    """Get descriptive text for each theme."""
    descriptions = {
        'cultural_events': 'Festivals, performances, concerts, and exhibitions that celebrate Austin\'s diverse culture',
        'community_spaces': 'Art spaces, galleries, studios, and creative venues accessible to the community',
        'accessibility': 'Ensuring arts and culture are inclusive and accessible to all residents',
        'public_art': 'Murals, sculptures, installations, and street art that enhance public spaces',
        'cultural_preservation': 'Protecting and celebrating Austin\'s cultural heritage, traditions, and history',
        'digital_arts': 'Digital art, technology-based creativity, multimedia, and virtual experiences',
        'artist_support': 'Grants, residencies, stipends, and direct funding for artists',
        'arts_education': 'Art education programs, workshops, classes, and youth arts initiatives'
    }
    return descriptions.get(theme_key, '')

def main():
    """Main visualization function."""
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Load data
    data = load_analysis_results()
    
    # Create visualizations
    create_theme_bar_chart(data)
    create_geographic_visualization(data)
    
    # Prepare microsite data
    prepare_microsite_data(data)
    
    print("\n✓ Visualizations complete!")
    print("Generated files:")
    print("  - results/theme_percentages_chart.png")
    print("  - results/theme_percentages_chart.svg")
    print("  - results/geographic_distribution_chart.png")
    print("  - results/microsite_data.json")
    print("  - results/survey_data.js")

if __name__ == "__main__":
    main()