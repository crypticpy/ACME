# ACME Cultural Funding Analysis 2025

Research-grade analysis of Austin's cultural funding landscape using comprehensive survey data, qualitative feedback, and advanced AI-powered analysis.

## Overview

This project provides deep insights into Austin's cultural funding ecosystem through a phased, rigorous approach:

### Phase 1: Deep Analysis & Feature Extraction
- **Question-by-Question Analysis**: Each survey question analyzed individually to preserve context
- **Comprehensive Feature Extraction**: All 1,187 survey responses processed (not sampled)
- **Multi-dimensional Analysis**: Stakeholder classification, thematic analysis, sentiment analysis, urgency scoring
- **Persistent Storage**: All analysis results cached and stored for reuse

### Phase 2: Insight Generation & Reporting
- **Executive Report**: Data-driven insights with full methodology transparency
- **Visualization Suite**: Charts and graphics generated from stored analysis data
- **Statistical Rigor**: Confidence intervals, significance testing, and validation

### Phase 3: Public Communication
- **Interactive Microsite**: Modern web platform for public engagement
- **Data Transparency**: Full access to aggregated findings
- **Accessibility**: WCAG compliant for inclusive access

## Project Structure

```
acme-cultural-funding-2025/
├── analysis/          # Core Python analysis engine
├── data/             # Data pipeline (raw → processed → results)
├── report/           # Executive report generation
├── microsite/        # React-based public website
├── infrastructure/   # CI/CD and deployment configs
├── gpt_41.md         # GPT-4.1 API documentation and usage guide
└── structured_responses.md  # Structured outputs documentation
```

## Analysis Philosophy

This project follows academic research standards:
- **No Sampling**: Process ALL responses, not random subsets
- **Context Preservation**: Each question analyzed separately to maintain meaning
- **Full Traceability**: Every insight linked to source data
- **Reproducibility**: All analysis steps documented and repeatable
- **No Shortcuts**: Quality over speed at every step

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+  
- Poetry (Python package manager)
- OpenAI API key (GPT-4.1 access required - see `gpt_41.md` for model details)
- 16GB+ RAM recommended for full analysis

### Phase 1: Run Deep Analysis

```bash
# Setup environment
cd analysis
cp .env.example .env  # Add your OpenAI API key
poetry install

# Run question-by-question analysis (2-3 hours)
poetry run python run_deep_analysis.py

# Results stored in:
# - data/analysis_features/  (extracted features)
# - data/llm_cache/         (LLM responses)
# - data/results/           (aggregated insights)
```

### Phase 2: Generate Reports

```bash
# Generate visualizations from stored analysis
poetry run python generate_visualizations.py

# Create executive report
poetry run python generate_report.py
```

### Phase 3: Launch Microsite

```bash
cd ../microsite
npm install
npm run dev  # Local development
npm run build  # Production build
```

## Data Sources

- **Community Survey**: 1,187 responses on arts/culture engagement
- **Working Document**: 1,394 feedback items from various stakeholder sessions
- **Programs Analyzed**: Nexus, Thrive, Elevate, Austin Live Music Fund, Art in Public Places, Creative Space Assistance Program

## Key Features

### Analysis Pipeline
- Automated data validation with full audit trail
- Statistical analysis with confidence intervals
- AI-powered thematic analysis using GPT-4
- Program-specific deep dives
- Transportation/parking lot analysis

### Executive Report
- Professional design with custom branding
- Interactive charts and infographics
- Methodology transparency
- Actionable recommendations

### Public Microsite
- Modern React/TypeScript architecture
- Accessible (WCAG AAA compliant)
- Interactive data visualizations
- Mobile-responsive design
- SEO optimized

## Methodology

### Question-by-Question Deep Analysis
Each survey question is analyzed individually using GPT-4.1 with structured outputs (see `gpt_41.md` and `structured_responses.md` for API documentation) to extract:
- **Key Themes**: Major topics and patterns specific to that question
- **Sentiment Analysis**: Positive, negative, neutral, or mixed sentiment
- **Urgency Scoring**: High, medium, or low urgency for action
- **Stakeholder Perspectives**: How different groups (artists, organizations, residents) respond
- **Direct Quotes**: Representative verbatim responses for evidence

### Multi-Pass Processing
1. **First Pass**: Extract features from each individual response
2. **Second Pass**: Aggregate patterns within each question
3. **Third Pass**: Cross-question synthesis and validation
4. **Fourth Pass**: Statistical validation and confidence scoring

### Storage Architecture
- **Feature Store**: Structured data warehouse of all extracted features
- **LLM Cache**: Complete record of all AI analysis (SHA-256 keyed)
- **Audit Trail**: Full lineage from raw data to final insight
- **Version Control**: All analysis iterations preserved

### Quality Assurance
- **No Sampling**: 100% of responses analyzed (not random subsets)
- **Context Preservation**: Question intent preserved throughout
- **Human Validation**: Key findings reviewed by domain experts
- **Statistical Rigor**: Proper confidence intervals and significance testing

## Security & Privacy

- PII removed from all processed data
- Secure credential management
- Data retention policies enforced
- GDPR/CCPA compliant

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

Copyright © 2025 ACME. All rights reserved.

## Contact

For questions or support, contact: [project-team@acme.gov]