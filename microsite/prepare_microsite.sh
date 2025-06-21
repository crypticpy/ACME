#!/bin/bash

# Prepare microsite with data files

echo "Preparing microsite data..."

# Create data directory
mkdir -p data

# Copy JSON data files
cp ../analysis/data/results/cultural_funding_analysis/cultural_funding_themes.json data/
cp ../analysis/data/results/cultural_funding_analysis/program_themes_analysis.json data/

# Copy chart image
cp ../analysis/data/results/cultural_funding_analysis/cultural_funding_themes_pie_chart.png data/

# Copy Word report
cp ../analysis/data/results/reports/ACME_Cultural_Funding_Report_LATEST.docx data/

echo "✓ Data files copied successfully"

# Create GitHub Pages config
cat > _config.yml << EOF
theme: jekyll-theme-minimal
title: ACME Cultural Funding Analysis 2025
description: Comprehensive Analysis of Austin's Cultural Funding Landscape
EOF

echo "✓ GitHub Pages config created"

# Create README for GitHub
cat > README.md << EOF
# ACME Cultural Funding Analysis 2025 - Microsite

This microsite presents the findings from a comprehensive analysis of Austin's cultural funding landscape.

## Key Findings

- **1,187** survey responses analyzed
- **67.7%** of respondents are creative professionals
- **10** key funding themes identified
- **6** cultural programs analyzed

## View the Site

Visit the live site at: [https://[your-username].github.io/acme-cultural-funding-2025/](https://[your-username].github.io/acme-cultural-funding-2025/)

## Report Download

The full Word document report is available for download from the microsite.

## Data Sources

- Community survey responses
- Working document recommendations
- Stakeholder feedback

## Technology

Built with:
- HTML5/CSS3
- Vanilla JavaScript
- GitHub Pages

EOF

echo "✓ README created"
echo "✓ Microsite preparation complete!"
echo ""
echo "To deploy:"
echo "1. Create a new GitHub repository"
echo "2. Push the microsite folder to the repository"
echo "3. Enable GitHub Pages in repository settings"
echo "4. Select 'main' branch and root folder"