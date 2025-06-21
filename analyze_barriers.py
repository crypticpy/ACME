import pandas as pd
import numpy as np
from collections import Counter
import re

# Read the Excel file
file_path = '/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx'
df = pd.read_excel(file_path)

# Focus on the main barriers column
barriers_col = 'What barriers, if any, prevent you from participating in arts and culture events in Austin? (Select all that apply.)'

print("=== ANALYZING BARRIER RESPONSES ===")
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
        print(f"  Options: {options}")
    else:
        print(f"  Contains semicolons: NO")

# Count responses with semicolons
total_responses = df[barriers_col].notna().sum()
semicolon_responses = df[barriers_col].dropna().apply(lambda x: ';' in str(x)).sum()
print(f"\n=== SEMICOLON ANALYSIS ===")
print(f"Responses with semicolons: {semicolon_responses} ({semicolon_responses/total_responses*100:.1f}%)")
print(f"Responses without semicolons: {total_responses - semicolon_responses} ({(total_responses - semicolon_responses)/total_responses*100:.1f}%)")

# Get all unique barriers mentioned
print("\n=== EXTRACTING ALL BARRIERS ===")
all_barriers = []
barrier_counts = Counter()

for response in df[barriers_col].dropna():
    if pd.isna(response) or response == 'None' or response == 'No barriers':
        continue
    
    # Split by semicolon if present
    if ';' in str(response):
        barriers = [b.strip() for b in str(response).split(';') if b.strip()]
    else:
        barriers = [str(response).strip()]
    
    for barrier in barriers:
        if barrier:  # Only count non-empty barriers
            all_barriers.append(barrier)
            barrier_counts[barrier] += 1

print(f"Total barrier mentions across all responses: {len(all_barriers)}")
print(f"Unique barriers mentioned: {len(barrier_counts)}")

# Show top 10 most common barriers
print("\n=== TOP 10 BARRIERS BY FREQUENCY ===")
for barrier, count in barrier_counts.most_common(10):
    print(f"{count}: {barrier}")