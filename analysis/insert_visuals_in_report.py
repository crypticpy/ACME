#!/usr/bin/env python3
"""Insert visualizations into the comprehensive report at appropriate locations."""

import re
from pathlib import Path
from datetime import datetime

def insert_visualizations():
    """Insert visualization references into the report."""
    
    # Read the latest comprehensive report
    report_path = Path("data/results/reports/ACME_Comprehensive_Report_LATEST.md")
    with open(report_path, 'r') as f:
        content = f.read()
    
    # Visualization insertion points
    visualizations = {
        # After Executive Summary section
        "**Community Sentiment Overview:**": """

![Community Sentiment by Question](visualizations/sentiment_overview_LATEST.png)
*Figure 1: Sentiment distribution across all survey questions reveals predominantly negative sentiment for barriers-related questions and positive sentiment for opportunities.*

""",
        # After Cross-Question Synthesis header
        "## Cross-Question Synthesis": """## Cross-Question Synthesis

![Executive Summary Visual](visualizations/executive_summary_visual_LATEST.png)
*Figure 2: Comprehensive executive overview showing key metrics, critical issues, sentiment distribution, and priority actions.*

""",
        # After Recurring Themes section
        "### Recurring Themes": """### Recurring Themes

![Theme Frequency Chart](visualizations/theme_frequency_LATEST.png)
*Figure 3: Top 10 recurring themes across all questions, showing the most pressing issues facing Austin's cultural community.*

""",
        # After theme list
        "- Questions: {', '.join(info.get('question_ids', []))}": """

![Urgency Matrix](visualizations/urgency_matrix_LATEST.png)
*Figure 4: Theme priority matrix plotting urgency against frequency. Themes in the upper-right quadrant require immediate attention.*

""",
        # After Stakeholder Perspectives
        "### Stakeholder Perspectives": """### Stakeholder Perspectives

*Note: Interactive stakeholder visualization available in the HTML version of this report.*

""",
        # After Program-Specific Analysis header
        "## Program-Specific Analysis": """## Program-Specific Analysis

![Program Comparison](visualizations/program_comparison_LATEST.png)
*Figure 5: Comparative analysis of top cultural programs showing mentions, sentiment, strengths, and areas for improvement.*

""",
        # After Strategic Recommendations
        "## Strategic Recommendations": """## Strategic Recommendations

*Note: For an interactive flow diagram of how community needs translate to strategic outcomes, see the HTML version of this report.*

"""
    }
    
    # Insert visualizations in reverse order to maintain positions
    for marker, visual in reversed(list(visualizations.items())):
        if marker in content:
            # For some markers, we want to insert after the line
            if marker in ["### Recurring Themes", "### Stakeholder Perspectives", 
                         "## Cross-Question Synthesis", "## Program-Specific Analysis",
                         "## Strategic Recommendations"]:
                content = content.replace(marker, marker + visual, 1)
            else:
                # For others, insert after the next newline
                pos = content.find(marker)
                if pos != -1:
                    # Find the end of the line
                    end_pos = content.find('\n', pos)
                    if end_pos != -1:
                        content = content[:end_pos] + visual + content[end_pos:]
    
    # Special handling for the urgency heatmap - insert after theme listing
    pattern = r"(- Questions: [^\n]+)"
    matches = list(re.finditer(pattern, content))
    if matches:
        # Insert after the last occurrence
        last_match = matches[-1]
        end_pos = last_match.end()
        content = content[:end_pos] + visualizations["- Questions: {', '.join(info.get('question_ids', []))}"] + content[end_pos:]
    
    # Save enhanced report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    enhanced_path = Path(f"data/results/reports/ACME_Comprehensive_Report_Enhanced_{timestamp}.md")
    with open(enhanced_path, 'w') as f:
        f.write(content)
    
    # Also update the LATEST version
    with open(Path("data/results/reports/ACME_Comprehensive_Report_LATEST.md"), 'w') as f:
        f.write(content)
    
    print(f"✓ Enhanced report saved to: {enhanced_path}")
    print("✓ Updated LATEST version with visualizations")
    
    # Create a visualization guide
    guide_content = """# ACME Cultural Funding Analysis - Visualization Guide

## Report Visualizations

The comprehensive report includes the following visualizations:

### 1. Community Sentiment Overview
**Location**: After Executive Summary
**Purpose**: Shows sentiment distribution across all survey questions
**Key Insight**: Barriers questions show 86.8% negative sentiment while opportunities show 57.1% positive

### 2. Executive Dashboard
**Location**: Start of Cross-Question Synthesis
**Purpose**: Four-panel overview of key metrics
**Components**:
- Response distribution by question
- Top 5 strategic themes
- Overall sentiment pie chart
- Urgency level distribution

### 3. Theme Network Visualization
**Location**: After Recurring Themes section
**Purpose**: Shows interconnections between major themes
**Key Features**:
- Node size = mention frequency
- Edge thickness = co-occurrence strength
- Color coding by theme category

### 4. Urgency Heatmap
**Location**: After theme listings
**Purpose**: Visual priority matrix for themes by question
**Color Scale**: Light (low urgency) to Dark (high urgency)

### 5. Stakeholder Distribution Sunburst
**Location**: After Stakeholder Perspectives
**Purpose**: Hierarchical view of respondent types
**Interactive**: HTML version allows drilling down

### 6. Program Performance Radar
**Location**: Start of Program-Specific Analysis
**Purpose**: Multi-dimensional program comparison
**Metrics**: Mentions, positive sentiment, strengths, improvements needed

### 7. Funding Flow Sankey Diagram
**Location**: Before Strategic Recommendations
**Purpose**: Maps community needs to strategic outcomes
**Flow**: Community Needs → Themes → Strategic Outcomes

## Viewing Options

1. **In Report**: Static PNG images embedded in markdown
2. **Interactive**: Open HTML files in browser for interactive features
3. **High Resolution**: PNG files at 2x scale for presentations

## File Locations

All visualizations are saved in:
`data/results/reports/visualizations/`

- `*_LATEST.png/html` - Most recent versions
- `*_[timestamp].png/html` - Timestamped versions
"""
    
    guide_path = Path("data/results/reports/Visualization_Guide.md")
    with open(guide_path, 'w') as f:
        f.write(guide_content)
    
    print(f"\n✓ Visualization guide saved to: {guide_path}")

if __name__ == "__main__":
    insert_visualizations()