#!/usr/bin/env python3
"""Inspect survey data columns to find text responses."""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.ingestion.loader import DataLoader
from src.validation.audit import AuditLogger

def inspect_columns():
    """Inspect the survey data columns."""
    print("Loading survey data...")
    
    loader = DataLoader()
    data = loader.load_all_data()
    
    survey_df = data.get("survey")
    
    if survey_df is None:
        print("No survey data found!")
        return
    
    print(f"\nSurvey shape: {survey_df.shape}")
    print(f"Total rows: {len(survey_df)}")
    print(f"Total columns: {len(survey_df.columns)}")
    
    print("\nColumn names:")
    for i, col in enumerate(survey_df.columns):
        print(f"{i}: {col}")
    
    print("\nLooking for text columns...")
    text_columns = []
    for col in survey_df.columns:
        # Check data type and sample values
        sample_values = survey_df[col].dropna().head()
        if not sample_values.empty:
            # Check if values are string type and reasonably long
            if survey_df[col].dtype == 'object':
                avg_length = survey_df[col].dropna().astype(str).str.len().mean()
                if avg_length > 50:  # Likely text responses
                    text_columns.append(col)
                    print(f"\nPotential text column: {col}")
                    print(f"  Average length: {avg_length:.0f} chars")
                    print(f"  Sample: {survey_df[col].dropna().iloc[0][:100]}...")

if __name__ == "__main__":
    inspect_columns()