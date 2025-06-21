#!/usr/bin/env python3
"""Create visualization for funding themes by respondent percentage."""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_visualization():
    """Create bar chart of funding themes by respondent percentage."""
    
    # Load the data
    with open('results/funding_themes_by_respondent.json') as f:
        data = json.load(f)
    
    # Extract themes and percentages
    themes = []
    percentages = []
    counts = []
    
    # Sort by percentage
    sorted_themes = sorted(data['funding_themes'].items(), 
                          key=lambda x: x[1]['percentage'], reverse=True)
    
    for theme, info in sorted_themes:
        themes.append(theme)
        percentages.append(info['percentage'])
        counts.append(info['count'])
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create bars
    bars = plt.barh(themes, percentages, color='#3b82f6')
    
    # Add percentage and count labels
    for i, (bar, pct, count) in enumerate(zip(bars, percentages, counts)):
        # Percentage at end of bar
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{pct:.1f}%', va='center', fontsize=11, fontweight='bold')
        # Count inside bar
        plt.text(1, bar.get_y() + bar.get_height()/2, 
                f'{count} respondents', va='center', color='white', fontsize=10)
    
    # Styling
    plt.xlabel('Percentage of Respondents', fontsize=12)
    plt.title('Cultural Funding Themes: What the Community Wants\n' + 
              f'Based on {data["total_respondents"]} survey respondents', 
              fontsize=16, pad=20)
    
    # Add grid
    plt.grid(axis='x', alpha=0.3)
    
    # Set x-axis limit
    plt.xlim(0, max(percentages) + 5)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path = Path('results/funding_themes_by_respondent.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Visualization saved to: {output_path}")
    
    # Also create a simplified version for the microsite
    plt.figure(figsize=(10, 6))
    
    # Use only top 5 themes for microsite
    top_5_themes = themes[:5]
    top_5_percentages = percentages[:5]
    top_5_counts = counts[:5]
    
    # Shorten theme names for display
    display_names = {
        'Increase Funding Awareness': 'Better Communication',
        'Simplify Application Process': 'Simpler Applications',
        'Funding Transparency': 'Clear Decisions',
        'Equitable Distribution': 'Equitable Access',
        'Fair Artist Compensation': 'Fair Pay'
    }
    
    short_names = [display_names.get(t, t) for t in top_5_themes]
    
    bars = plt.barh(short_names, top_5_percentages, color='#3b82f6')
    
    for bar, pct, count in zip(bars, top_5_percentages, top_5_counts):
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{pct:.1f}%', va='center', fontsize=12, fontweight='bold')
    
    plt.xlabel('Percentage of Respondents', fontsize=12)
    plt.title('Top 5 Community Priorities for Cultural Funding', fontsize=14)
    plt.xlim(0, 30)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    microsite_path = Path('../docs/data/funding_priorities_chart.png')
    plt.savefig(microsite_path, dpi=150, bbox_inches='tight')
    print(f"✓ Microsite version saved to: {microsite_path}")
    
    # Create JSON for microsite
    microsite_data = {
        'analysis_date': data['analysis_date'],
        'total_respondents': data['total_respondents'],
        'top_themes': []
    }
    
    for theme, info in sorted_themes[:10]:
        microsite_data['top_themes'].append({
            'theme': theme,
            'display_name': display_names.get(theme, theme),
            'count': info['count'],
            'percentage': info['percentage'],
            'description': info['description']
        })
    
    microsite_json_path = Path('../docs/data/funding_priorities.json')
    with open(microsite_json_path, 'w') as f:
        json.dump(microsite_data, f, indent=2)
    print(f"✓ Microsite data saved to: {microsite_json_path}")

if __name__ == "__main__":
    create_visualization()