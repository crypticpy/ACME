#!/bin/bash
# Copy analysis data to microsite

echo "Copying analysis data to microsite..."

# Source and destination paths
ANALYSIS_DIR="../analysis/data/results"
MICROSITE_PUBLIC_DIR="../microsite/public/data"

# Create data directory if it doesn't exist
mkdir -p "$MICROSITE_PUBLIC_DIR"

# Find the most recent analysis results
LATEST_SESSION=$(ls -td "$ANALYSIS_DIR"/session_* 2>/dev/null | head -1)

if [ -z "$LATEST_SESSION" ]; then
    echo "No analysis results found. Please run the analysis first."
    exit 1
fi

echo "Using analysis results from: $LATEST_SESSION"

# Find microsite data file
MICROSITE_DATA=$(find "$LATEST_SESSION" -name "microsite_data.json" 2>/dev/null | head -1)

if [ -z "$MICROSITE_DATA" ]; then
    echo "No microsite_data.json found in the latest session."
    echo "Looking for visualization data..."
    
    # Try to find visualization data as fallback
    VIZ_DATA=$(find "$LATEST_SESSION" -name "analysis_data.json" 2>/dev/null | head -1)
    
    if [ -z "$VIZ_DATA" ]; then
        echo "No analysis data found. Please ensure the analysis pipeline completed successfully."
        exit 1
    fi
    
    echo "Using analysis_data.json as fallback"
    cp "$VIZ_DATA" "$MICROSITE_PUBLIC_DIR/microsite_data.json"
else
    cp "$MICROSITE_DATA" "$MICROSITE_PUBLIC_DIR/microsite_data.json"
fi

# Copy visualization files if they exist
VIZ_DIR="$LATEST_SESSION/visualizations"
if [ -d "$VIZ_DIR" ]; then
    echo "Copying visualization files..."
    mkdir -p "$MICROSITE_PUBLIC_DIR/visualizations"
    
    # Copy only web-friendly formats
    find "$VIZ_DIR" -name "*.html" -o -name "*.json" | while read -r file; do
        cp "$file" "$MICROSITE_PUBLIC_DIR/visualizations/"
    done
fi

echo "Data copy complete!"
echo "Files copied to: $MICROSITE_PUBLIC_DIR"

# Show what was copied
echo -e "\nCopied files:"
ls -la "$MICROSITE_PUBLIC_DIR"