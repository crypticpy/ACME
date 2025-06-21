#!/usr/bin/env python3
"""Quick script to inspect Excel columns."""

import pandas as pd
from pathlib import Path

# Load survey file
survey_file = Path("data/raw/ACME_Community_Survey.xlsx")
df = pd.read_excel(survey_file, nrows=5)

print("Survey columns:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print(f"\nTotal columns: {len(df.columns)}")
print(f"Shape: {df.shape}")

# Load working doc
working_file = Path("data/raw/ACME_Working_Document.xlsx") 
xl = pd.ExcelFile(working_file)
print(f"\nWorking document sheets: {xl.sheet_names}")

# Check first sheet
df_work = pd.read_excel(working_file, sheet_name=xl.sheet_names[0], nrows=5)
print(f"\nFirst sheet columns ({xl.sheet_names[0]}):")
for i, col in enumerate(df_work.columns):
    print(f"{i}: {col}")