import pandas as pd
import numpy as np
from collections import Counter
import re

# Read the Excel file
file_path = '/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx'
df = pd.read_excel(file_path)

# First, let's examine the structure of the data
print("=== SURVEY DATA STRUCTURE ===")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nColumn names:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n=== FIRST 5 ROWS PREVIEW ===")
print(df.head())

# Check for geographic data (ZIP codes, addresses, etc.)
print("\n=== GEOGRAPHIC DATA CHECK ===")
geographic_keywords = ['zip', 'ZIP', 'address', 'Address', 'location', 'Location', 'city', 'City', 'neighborhood']
geo_columns = [col for col in df.columns if any(keyword in str(col) for keyword in geographic_keywords)]
print(f"Geographic columns found: {geo_columns}")

# Look for barrier/challenge related columns
print("\n=== BARRIER/CHALLENGE COLUMNS ===")
barrier_keywords = ['barrier', 'challenge', 'difficulty', 'obstacle', 'prevent', 'stop', 'access']
barrier_columns = [col for col in df.columns if any(keyword.lower() in str(col).lower() for keyword in barrier_keywords)]
print(f"Barrier-related columns found: {barrier_columns}")

# Check the format of responses in the first barrier column if found
if barrier_columns:
    first_barrier_col = barrier_columns[0]
    print(f"\n=== RESPONSE FORMAT CHECK for '{first_barrier_col}' ===")
    # Show first 10 non-null responses
    non_null_responses = df[first_barrier_col].dropna().head(10)
    for i, response in enumerate(non_null_responses):
        print(f"Response {i+1}: {response}")
    
    # Check if responses contain semicolons (multiple choice format)
    semicolon_responses = df[first_barrier_col].dropna().apply(lambda x: ';' in str(x)).sum()
    print(f"\nResponses containing semicolons: {semicolon_responses} out of {df[first_barrier_col].notna().sum()}")

# Save basic info to understand the data better
print("\n=== DATA TYPES ===")
print(df.dtypes)