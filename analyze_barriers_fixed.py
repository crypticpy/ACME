import pandas as pd
import numpy as np
from collections import Counter
import re

# Read the Excel file
file_path = '/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx'
df = pd.read_excel(file_path)

# Find the exact barrier column name
barrier_columns = [col for col in df.columns if 'barriers' in col.lower() and 'prevent' in col.lower()]
print(f"Found barrier columns: {barrier_columns}")

if barrier_columns:
    barriers_col = barrier_columns[0]
else:
    # Try another approach
    for col in df.columns:
        if 'What barriers' in str(col):
            barriers_col = col
            break

print(f"\nUsing column: '{barriers_col}'")

print("\n=== ANALYZING BARRIER RESPONSES ===")
print(f"Total respondents: {len(df)}")
print(f"Respondents who answered barriers question: {df[barriers_col].notna().sum()}")

# Check the format of responses - look for semicolons
print("\n=== CHECKING RESPONSE FORMAT ===")
# Get sample of responses
sample_responses = df[barriers_col].dropna().head(20)
for i, response in enumerate(sample_responses):
    print(f"\nResponse {i+1}:")
    print(f"  Raw: {repr(response)}")
    if ';' in str(response):
        print(f"  Contains semicolons: YES")
        options = [opt.strip() for opt in str(response).split(';')]
        print(f"  Number of options selected: {len(options)}")
        for j, opt in enumerate(options):
            print(f"    Option {j+1}: {opt}")

# Count responses with semicolons
total_responses = df[barriers_col].notna().sum()
semicolon_responses = df[barriers_col].dropna().apply(lambda x: ';' in str(x)).sum()
print(f"\n=== SEMICOLON ANALYSIS ===")
print(f"Responses with semicolons: {semicolon_responses} ({semicolon_responses/total_responses*100:.1f}%)")
print(f"Responses without semicolons: {total_responses - semicolon_responses} ({(total_responses - semicolon_responses)/total_responses*100:.1f}%)")