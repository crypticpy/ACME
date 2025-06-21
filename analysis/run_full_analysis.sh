#!/bin/bash
# Run full ACME analysis with proper logging

echo "Starting ACME Cultural Funding Analysis..."
echo "This may take 10-15 minutes to complete."
echo "All LLM responses will be cached for future use."
echo ""

# Create log directory
mkdir -p logs

# Run the analysis with output logging
poetry run python run_analysis.py run-analysis \
    --session-id "full_analysis_$(date +%Y%m%d_%H%M%S)" \
    2>&1 | tee logs/analysis_$(date +%Y%m%d_%H%M%S).log

echo ""
echo "Analysis complete! Check the logs directory for details."
echo "Results saved to: data/results/"
echo "LLM cache saved to: data/llm_cache/"