# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

When you arrive at [feature] your first inclination will be to pattern match on learned behaviors which will typically result in you mocking functionality. Instead of mocking, understand that the cumulative reward of finishing this with real functionality means you can move onto learning new things and working on new projects thereafter. It is extremely unethical and dangerous to produce placeholders, hacks, incomplete code, fake tests or work arounds in production code. This behavior could get people fired, and pose substantial risk if it gets pushed into production. You need to focus on delivering complete features and performing at a high level of competence without taking shortcuts or the path of least resistence. Track your progress well. Test your features, research on the internet when you dont know things, and DO NOT take your own initiative to make subsantial changes from the requirements. Just do your best to implement what is asked and don't get over zealous. It can cause more harm than good and we don't want that. 

## CRITICAL: Ethical Data Handling Requirements

**This project analyzes real feedback from real people in Austin's cultural community. Their voices and experiences matter.**

### Mandatory Requirements:

1. **NEVER use mock data, fake tests, fake results, or mock results**
2. **NEVER take shortcuts in analysis or testing** - always root cause issues
3. **ALWAYS work with real data and implement real functionality**
4. **ALWAYS maintain data integrity** - these insights impact funding decisions affecting real artists and organizations
5. **ALWAYS preserve the actual voices** in the data - no synthetic or generated responses

### GPT-4.1 Model Standards

When working with any LLM integration code:

- **Azure OpenAI is the primary provider** - The system now uses Azure OpenAI endpoints with automatic fallback to standard OpenAI
- **Maintain GPT-4.1 compatibility** per the documentation in `gpt_41.md` and `structured_responses.md`
- **Use structured outputs** with Pydantic models for all LLM responses
- **Implement proper response validation** - never accept malformed LLM outputs
- **Follow the JSON schema patterns** defined in PROJECT_PLAN.md
- **Cache all LLM responses** but never fabricate cached data

Remember: This analysis influences how cultural funding is distributed in Austin. Every shortcut or mock data point undermines the community members who shared their experiences.

## Project Overview

This is the ACME Cultural Funding Analysis project - a research-grade analysis of Austin's cultural funding landscape using comprehensive survey data and AI-powered analysis. The project has three main phases:

1. **Analysis Pipeline** (Python) - Deep feature extraction and LLM-based analysis
2. **Report Generation** (Python) - Executive reports with visualizations
3. **Public Microsite** (React/Next.js) - Interactive web platform for findings

## Azure OpenAI Setup

The system now uses Azure OpenAI as the primary LLM provider with automatic fallback to standard OpenAI.

To configure Azure OpenAI:
1. Copy `.env.example` to `.env`
2. Set the following environment variables:
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT-4.1 deployment name
   - `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)

To test the connection:
```bash
cd analysis
poetry run python test_azure_openai.py
```

## Commands

### Analysis Pipeline

```bash
# Setup and run full analysis (2-3 hours with LLM calls)
cd analysis
cp .env.example .env  # Add Azure OpenAI credentials
poetry install
poetry run python run_analysis.py run-analysis

# Run deep qualitative analysis with GPT-4.1 structured outputs
poetry run python run_deep_analysis.py

# Generate visualizations for deep analysis results
poetry run python run_deep_visualizations.py

# Run visualizations only (using cached results)
poetry run python run_visualizations.py

# Question-by-question deep analysis
poetry run python analyze_by_question.py
```

### Microsite

```bash
cd microsite
npm install
npm run dev        # Start development server
npm run build      # Production build
npm run lint       # Run ESLint
npm run type-check # TypeScript checking
```

### Data Transfer

```bash
# Copy analysis results to microsite
cd scripts
./copy_analysis_data.sh
```

## Architecture

### Analysis Module Structure

The analysis engine (`analysis/src/`) follows a pipeline architecture:

- **ingestion/** - Data validation and loading from Excel files
- **llm/** - OpenAI client with SHA-256 caching and structured prompts
- **qualitative/** - Theme extraction, sentiment analysis, urgency scoring
- **quantitative/** - Demographics, participation metrics, statistical analysis
- **features/** - Deep feature extraction using GPT-4.1 structured outputs
  - ResponseFeatureExtractor - Extract multi-dimensional features per response
  - QuestionAnalyzer - Aggregate patterns at question level
  - CrossQuestionSynthesizer - Identify meta-themes across questions
  - ProgramAnalyzer - Extract program-specific feedback
- **visualization/** - Chart generation (matplotlib, plotly, seaborn)
- **reporting/** - Word document generation with embedded visualizations
- **validation/** - Comprehensive audit logging and data lineage tracking

### Key Design Patterns

1. **Pydantic Configuration**: All settings managed via `src/config.py` with env variable support
2. **LLM Caching**: All OpenAI calls cached by content hash to `data/llm_cache/`
3. **Audit Trail**: Every operation logged via `AuditLogger` for reproducibility
4. **Two-Track Analysis**:
   - WHO track: Demographics and participation data
   - WHAT track: Qualitative feedback and themes
5. **Result Storage**: JSON outputs with timestamps in `data/results/`

### Data Flow

```text
data/raw/*.xlsx → ingestion → processed/ → analysis → results/ → visualizations/ → report/
                                              ↓
                                         llm_cache/
```

## GPT-4.1 Integration Plan

The PROJECT_PLAN.md describes transitioning to GPT-4.1 with structured outputs (references `gpt_41.md` and `structured_responses.md`). Key implementation notes:

- Use OpenAI Responses API with Pydantic models for type-safe outputs
- Implement ResponseFeatures, QuestionAnalysis, CrossQuestionInsight schemas
- Process responses in batches with XML delimiters for 1M token context
- Add persistence/planning/accuracy reminders for agentic behavior

Current implementation uses gpt-4o-2024-08-06, configured in `analysis/src/llm/client.py`.

## Development Notes

- **No Test Suite**: Project lacks automated tests - consider adding pytest tests when implementing new features
- **Programs Analyzed**: Nexus, Thrive, Elevate, Austin Live Music Fund, Art in Public Places, Creative Space Assistance Program
- **Question-by-Question Analysis**: Run `analyze_by_question.py` for deep per-question insights (separate from main pipeline)
- **Microsite Data**: After analysis, use `copy_analysis_data.sh` to update microsite with real data

## Common Issues

1. **OpenAI API Key**: Ensure OPENAI_API_KEY is set in analysis/.env
2. **Memory Usage**: Full analysis requires 16GB+ RAM due to large dataset processing
3. **API Costs**: Full LLM analysis costs ~$50-100 in OpenAI API fees
4. **Caching**: Delete `data/llm_cache/` to force fresh LLM analysis
