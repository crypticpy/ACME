# ACME Cultural Funding Survey Analysis

## Overview

This analysis provides accurate percentages of unique respondents who mentioned each cultural funding theme in the ACME Community Survey. The analysis ensures each respondent is counted only once per theme, regardless of how many times they mentioned it across multiple survey questions.

## Key Findings

Based on 1,187 survey respondents:

1. **Cultural Events** - 93.26% (1,107 respondents)
   - Highest priority theme
   - Includes festivals, performances, concerts, exhibitions

2. **Community Spaces** - 84.92% (1,008 respondents)
   - Strong demand for accessible creative venues
   - Galleries, studios, art spaces

3. **Accessibility** - 81.63% (969 respondents)
   - Critical focus on inclusive arts access
   - Ensuring all residents can participate

4. **Public Art** - 77.34% (918 respondents)
   - Murals, sculptures, installations
   - Enhancement of public spaces

5. **Cultural Preservation** - 77.09% (915 respondents)
   - Protecting Austin's cultural heritage
   - Supporting traditions and history

6. **Digital Arts** - 40.02% (475 respondents)
   - Growing interest in technology-based art
   - Virtual and multimedia experiences

7. **Artist Support** - 21.31% (253 respondents)
   - Direct funding for artists
   - Grants, residencies, stipends

8. **Arts Education** - 9.86% (117 respondents)
   - Workshops, classes, youth programs
   - Teaching and learning opportunities

## Geographic Coverage

- 1,151 respondents (96.97%) provided valid ZIP codes
- 83 different ZIP codes represented
- Top 5 ZIP codes: 78745, 78704, 78702, 78723, 78751

## Methodology

1. **Data Source**: ACME_Community_Survey.xlsx (1,187 responses)
2. **Analysis Approach**: 
   - Searched all text response columns for theme keywords
   - Each respondent counted only once per theme
   - Case-insensitive keyword matching
3. **Theme Keywords**: Predefined sets of related terms for each theme
4. **Geographic Analysis**: Cleaned and validated ZIP codes

## Files Generated

### Analysis Scripts
- `calculate_respondent_percentages.py` - Main analysis script
- `visualize_theme_percentages.py` - Visualization generation

### Results
- `results/respondent_theme_analysis.json` - Complete analysis data
- `results/theme_percentages_summary.csv` - Summary table
- `results/analysis_report.md` - Detailed report
- `results/microsite_data.json` - Web-ready data format
- `results/survey_data.js` - JavaScript module for web integration

### Visualizations
- `results/theme_percentages_chart.png` - Bar chart of themes
- `results/theme_percentages_chart.svg` - Vector format chart
- `results/geographic_distribution_chart.png` - Top ZIP codes

## Usage for Microsite

The `microsite_data.json` file contains clean, structured data ready for web integration:
- Survey statistics
- Theme percentages and counts
- Theme descriptions
- All data sorted by popularity

The `survey_data.js` file can be directly imported into the microsite as an ES6 module.

## Running the Analysis

```bash
# Run the main analysis
python calculate_respondent_percentages.py

# Generate visualizations
python visualize_theme_percentages.py
```

## Data Integrity

- Analysis counts each unique respondent only once per theme
- All percentages based on total respondent count (1,187)
- Geographic data validated for proper ZIP code format
- Results triple-checked for accuracy