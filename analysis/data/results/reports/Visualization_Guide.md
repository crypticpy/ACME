# ACME Cultural Funding Analysis - Visualization Guide

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
