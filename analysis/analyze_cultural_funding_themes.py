#!/usr/bin/env python3
"""Re-analyze themes specifically focused on Cultural Funding."""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

def load_survey_responses():
    """Load original survey responses for cultural funding analysis."""
    # Load from the NEW_Data Excel file
    survey_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx")
    df = pd.read_excel(survey_path)
    
    # Find columns related to cultural funding
    funding_columns = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['fund', 'support', 'improve', 'barrier', 'challenge', 'need']):
            funding_columns.append(col)
    
    print(f"Found {len(funding_columns)} columns related to cultural funding:")
    for col in funding_columns[:5]:  # Show first 5
        print(f"  - {col}")
    
    return df, funding_columns

def extract_funding_themes(df, columns):
    """Extract themes specifically related to cultural funding."""
    
    # Keywords that indicate cultural funding topics
    funding_keywords = {
        'increase_funding': ['increase fund', 'more fund', 'additional fund', 'raise fund', 'expand fund', 'funding increase'],
        'grant_access': ['grant application', 'grant process', 'grant access', 'apply for grant', 'grant requirement'],
        'equitable_distribution': ['equitable', 'equity', 'fair distribution', 'equal access', 'inclusive fund'],
        'application_process': ['application', 'apply', 'paperwork', 'process', 'bureaucracy', 'red tape'],
        'transparency': ['transparent', 'transparency', 'clear criteria', 'understand', 'clarity'],
        'small_org_support': ['small organization', 'emerging', 'grassroots', 'startup', 'new organization'],
        'artist_compensation': ['artist pay', 'fair pay', 'compensation', 'living wage', 'payment'],
        'multi_year_funding': ['multi-year', 'sustainable', 'long-term', 'ongoing fund', 'recurring'],
        'reporting_burden': ['reporting', 'documentation', 'report requirement', 'administrative burden'],
        'funding_awareness': ['aware', 'know about', 'information', 'outreach', 'communication']
    }
    
    # Analyze each response
    theme_counts = Counter()
    theme_examples = {theme: [] for theme in funding_keywords}
    
    for col in columns:
        if col not in df.columns:
            continue
            
        for response in df[col].dropna():
            response_lower = str(response).lower()
            
            # Check for each theme
            for theme, keywords in funding_keywords.items():
                if any(keyword in response_lower for keyword in keywords):
                    theme_counts[theme] += 1
                    if len(theme_examples[theme]) < 5:  # Collect up to 5 examples
                        theme_examples[theme].append(str(response)[:200])  # First 200 chars
    
    return theme_counts, theme_examples

def analyze_working_document_themes():
    """Extract cultural funding themes from the working document."""
    working_doc_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Working_Document.xlsx")
    
    # Load Database sheet which contains recommendations
    df = pd.read_excel(working_doc_path, sheet_name='Database')
    
    theme_counts = Counter()
    theme_examples = {
        'increase_funding': [],
        'grant_access': [],
        'equitable_distribution': [],
        'application_process': [],
        'transparency': [],
        'small_org_support': [],
        'artist_compensation': [],
        'multi_year_funding': [],
        'reporting_burden': [],
        'funding_awareness': []
    }
    
    # Analyze recommendations column
    if 'Recommendation' in df.columns:
        for rec in df['Recommendation'].dropna():
            rec_lower = str(rec).lower()
            
            # More detailed keyword matching for recommendations
            if any(word in rec_lower for word in ['increase', 'expand', 'more fund', 'additional']):
                theme_counts['increase_funding'] += 1
                if len(theme_examples['increase_funding']) < 5:
                    theme_examples['increase_funding'].append(str(rec))
            
            if any(word in rec_lower for word in ['grant', 'application', 'apply']):
                theme_counts['grant_access'] += 1
                if len(theme_examples['grant_access']) < 5:
                    theme_examples['grant_access'].append(str(rec))
            
            if any(word in rec_lower for word in ['equit', 'fair', 'inclusive', 'access']):
                theme_counts['equitable_distribution'] += 1
                if len(theme_examples['equitable_distribution']) < 5:
                    theme_examples['equitable_distribution'].append(str(rec))
            
            if any(word in rec_lower for word in ['simplif', 'streamline', 'process', 'easier']):
                theme_counts['application_process'] += 1
                if len(theme_examples['application_process']) < 5:
                    theme_examples['application_process'].append(str(rec))
            
            if any(word in rec_lower for word in ['transparen', 'clear', 'understand']):
                theme_counts['transparency'] += 1
                if len(theme_examples['transparency']) < 5:
                    theme_examples['transparency'].append(str(rec))
            
            if any(word in rec_lower for word in ['small', 'emerging', 'grassroot', 'startup']):
                theme_counts['small_org_support'] += 1
                if len(theme_examples['small_org_support']) < 5:
                    theme_examples['small_org_support'].append(str(rec))
            
            if any(word in rec_lower for word in ['pay', 'compensation', 'wage', 'artist fee']):
                theme_counts['artist_compensation'] += 1
                if len(theme_examples['artist_compensation']) < 5:
                    theme_examples['artist_compensation'].append(str(rec))
            
            if any(word in rec_lower for word in ['multi-year', 'sustain', 'long-term', 'ongoing']):
                theme_counts['multi_year_funding'] += 1
                if len(theme_examples['multi_year_funding']) < 5:
                    theme_examples['multi_year_funding'].append(str(rec))
    
    return theme_counts, theme_examples

def create_funding_pie_chart(theme_data: List[Tuple[str, int, float]]):
    """Create pie chart with both percentage and count labels."""
    
    # Prepare data
    themes = [item[0] for item in theme_data[:10]]  # Top 10
    counts = [item[1] for item in theme_data[:10]]
    total = sum(counts)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define colors
    colors = plt.cm.Set3(range(len(themes)))
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(counts, labels=themes, autopct='%1.1f%%',
                                       colors=colors, pctdistance=0.85,
                                       textprops={'fontsize': 10})
    
    # Add count labels
    for i, (wedge, count) in enumerate(zip(wedges, counts)):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = wedge.r * 0.7 * plt.np.cos(plt.np.radians(angle))
        y = wedge.r * 0.7 * plt.np.sin(plt.np.radians(angle))
        ax.text(x, y, f'n={count}', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Title
    ax.set_title('Top 10 Themes on Cultural Funding\n(Percentage and Count)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add total count
    ax.text(0, -1.3, f'Total mentions: {total:,}', ha='center', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.5))
    
    plt.tight_layout()
    return fig

def generate_cultural_funding_analysis():
    """Main function to generate cultural funding analysis."""
    
    print("=== CULTURAL FUNDING THEME ANALYSIS ===\n")
    
    # Load and analyze survey data
    print("1. Analyzing survey responses...")
    df, funding_columns = load_survey_responses()
    survey_themes, survey_examples = extract_funding_themes(df, funding_columns)
    
    # Analyze working document
    print("\n2. Analyzing working document recommendations...")
    doc_themes, doc_examples = analyze_working_document_themes()
    
    # Combine themes
    all_themes = Counter()
    all_themes.update(survey_themes)
    all_themes.update(doc_themes)
    
    # Format theme names
    theme_display_names = {
        'increase_funding': 'Increase Funding Levels',
        'grant_access': 'Improve Grant Access',
        'equitable_distribution': 'Equitable Distribution',
        'application_process': 'Simplify Application Process',
        'transparency': 'Funding Transparency',
        'small_org_support': 'Support Small Organizations',
        'artist_compensation': 'Fair Artist Compensation',
        'multi_year_funding': 'Multi-Year Funding',
        'reporting_burden': 'Reduce Reporting Burden',
        'funding_awareness': 'Increase Funding Awareness'
    }
    
    # Create sorted list with display names
    theme_data = []
    for theme, count in all_themes.most_common():
        display_name = theme_display_names.get(theme, theme.replace('_', ' ').title())
        percentage = (count / sum(all_themes.values())) * 100
        theme_data.append((display_name, count, percentage))
    
    # Generate results
    results = {
        "analysis_date": datetime.now().isoformat(),
        "total_survey_responses": len(df),
        "top_10_cultural_funding_themes": []
    }
    
    print("\n=== TOP 10 CULTURAL FUNDING THEMES ===")
    for i, (theme_name, count, percentage) in enumerate(theme_data[:10], 1):
        print(f"\n{i}. {theme_name}")
        print(f"   Count: {count} | Percentage: {percentage:.1f}%")
        
        # Get examples
        original_key = None
        for key, display in theme_display_names.items():
            if display == theme_name:
                original_key = key
                break
        
        examples = []
        if original_key:
            examples = survey_examples.get(original_key, []) + doc_examples.get(original_key, [])
            examples = [e for e in examples if e][:5]  # Get up to 5 non-empty examples
        
        theme_entry = {
            "rank": i,
            "theme": theme_name,
            "count": count,
            "percentage": round(percentage, 1),
            "supporting_sentences": examples[:3] if len(examples) >= 3 else examples + [""] * (3 - len(examples))
        }
        results["top_10_cultural_funding_themes"].append(theme_entry)
        
        if examples:
            print("   Supporting evidence:")
            for j, example in enumerate(examples[:3], 1):
                print(f"   {j}. {example[:150]}...")
    
    # Create visualization
    print("\n3. Creating pie chart visualization...")
    fig = create_funding_pie_chart(theme_data)
    
    # Save outputs
    output_dir = Path("data/results/cultural_funding_analysis")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save figure
    fig.savefig(output_dir / "cultural_funding_themes_pie_chart.png", dpi=300, bbox_inches='tight')
    fig.savefig(output_dir / "cultural_funding_themes_pie_chart.pdf", bbox_inches='tight')
    plt.close(fig)
    
    # Save JSON results
    with open(output_dir / "cultural_funding_themes.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save markdown summary
    summary_md = f"""# WHAT: Cultural Funding Thematic Analysis

**Generated:** {datetime.now().strftime('%B %d, %Y')}

## Top 10 Themes on Cultural Funding

![Cultural Funding Themes](cultural_funding_themes_pie_chart.png)

"""
    
    for theme_info in results["top_10_cultural_funding_themes"]:
        summary_md += f"""
### {theme_info['rank']}. {theme_info['theme']}
- **Frequency:** {theme_info['count']} mentions ({theme_info['percentage']}%)
- **Supporting Evidence:**
  1. {theme_info['supporting_sentences'][0] if theme_info['supporting_sentences'][0] else 'N/A'}
  2. {theme_info['supporting_sentences'][1] if theme_info['supporting_sentences'][1] else 'N/A'}
  3. {theme_info['supporting_sentences'][2] if theme_info['supporting_sentences'][2] else 'N/A'}
"""
    
    with open(output_dir / "WHAT_CULTURAL_FUNDING_ANALYSIS.md", 'w') as f:
        f.write(summary_md)
    
    print(f"\n✓ Analysis complete! Results saved to: {output_dir}")
    print("  - cultural_funding_themes_pie_chart.png")
    print("  - cultural_funding_themes.json")
    print("  - WHAT_CULTURAL_FUNDING_ANALYSIS.md")

if __name__ == "__main__":
    generate_cultural_funding_analysis()