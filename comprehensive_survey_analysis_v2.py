import pandas as pd
import numpy as np
from collections import Counter
import re

# Read the Excel file
file_path = '/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx'
df = pd.read_excel(file_path)

# Find the barriers column - handle special characters
barriers_col = None
for col in df.columns:
    if 'barriers' in col.lower() and 'prevent' in col.lower():
        barriers_col = col
        break

if not barriers_col:
    print("ERROR: Could not find barriers column")
    exit()

print("=" * 80)
print("ACME COMMUNITY SURVEY - COMPREHENSIVE BARRIER ANALYSIS")
print("=" * 80)

# Basic statistics
print(f"\nSURVEY OVERVIEW:")
print(f"Total survey respondents: {len(df)}")
print(f"Respondents who answered barriers question: {df[barriers_col].notna().sum()}")
print(f"Response rate for barriers question: {df[barriers_col].notna().sum()/len(df)*100:.1f}%")

# Analyze barrier responses
print("\n" + "=" * 80)
print("BARRIER ANALYSIS - PERCENTAGE OF RESPONDENTS")
print("=" * 80)

# Count unique respondents who mentioned each barrier
barrier_respondent_counts = Counter()
total_respondents_with_barriers = 0
transportation_details = Counter()
no_barrier_count = 0

for response in df[barriers_col].dropna():
    if pd.isna(response):
        continue
    
    # Check for "no barriers" responses
    response_str = str(response).strip().lower()
    if response_str in ['none', 'no barriers', 'n/a', 'na', '']:
        no_barrier_count += 1
        continue
    
    total_respondents_with_barriers += 1
    
    # Split by semicolon and clean
    barriers = [b.strip() for b in str(response).split(';') if b.strip()]
    
    # Count each unique barrier per respondent (only once per respondent)
    unique_barriers = set(barriers)
    for barrier in unique_barriers:
        # Skip empty strings or variations of "none"
        if barrier.lower() in ['none', 'no barriers', 'n/a', 'na', '']:
            continue
            
        barrier_respondent_counts[barrier] += 1
        
        # Track transportation subcategories
        if 'Transportation / parking' in barrier:
            transportation_details['Transportation/Parking (Combined)'] += 1
        elif 'parking' in barrier.lower():
            transportation_details['Parking (Mentioned Separately)'] += 1
        elif 'transit' in barrier.lower() or 'bus' in barrier.lower() or 'public transport' in barrier.lower():
            transportation_details['Public Transit (Specific)'] += 1

# Calculate percentages
print(f"\nRespondents who indicated 'No barriers': {no_barrier_count}")
print(f"Respondents who identified at least one barrier: {total_respondents_with_barriers}")
print(f"Total who answered the question: {total_respondents_with_barriers + no_barrier_count}")

print("\nBARRIER THEMES BY PERCENTAGE OF RESPONDENTS:")
print("-" * 80)
print(f"{'Barrier':<55} {'Count':<10} {'% of Those':<12} {'% of All':<10}")
print(f"{'':55} {'':10} {'w/ Barriers':<12} {'Respondents':<10}")
print("-" * 80)

# Sort by count and display
for barrier, count in barrier_respondent_counts.most_common():
    pct_of_barriers = (count / total_respondents_with_barriers) * 100
    pct_of_all = (count / len(df)) * 100
    barrier_display = barrier[:55]
    print(f"{barrier_display:<55} {count:<10} {pct_of_barriers:<12.1f} {pct_of_all:<10.1f}")

# Transportation breakdown
print("\n" + "=" * 80)
print("TRANSPORTATION BARRIER BREAKDOWN")
print("=" * 80)

# Count all transportation-related mentions
transport_respondents = set()
for idx, response in enumerate(df[barriers_col].dropna()):
    response_str = str(response).lower()
    if 'transport' in response_str or 'parking' in response_str:
        transport_respondents.add(idx)

transport_total = len(transport_respondents)
print(f"\nTotal respondents mentioning any transportation/parking issue: {transport_total}")
print(f"This represents {transport_total/total_respondents_with_barriers*100:.1f}% of those with barriers")
print(f"This represents {transport_total/len(df)*100:.1f}% of all survey respondents")

# Geographic analysis
print("\n" + "=" * 80)
print("GEOGRAPHIC ANALYSIS")
print("=" * 80)

zip_col = 'What zip code do you reside in?'
district_col = 'What Austin City Council District do you live in?'

# ZIP code analysis
print("\nZIP CODE DATA:")
valid_zips = df[zip_col].dropna()
print(f"Respondents who provided ZIP code: {len(valid_zips)} ({len(valid_zips)/len(df)*100:.1f}%)")

# Clean ZIP codes (remove any non-numeric characters)
cleaned_zips = []
zip_to_respondent = {}
for idx, z in enumerate(df[zip_col]):
    if pd.notna(z):
        # Extract 5-digit ZIP codes
        zip_match = re.search(r'\b\d{5}\b', str(z))
        if zip_match:
            zip_code = zip_match.group()
            cleaned_zips.append(zip_code)
            if zip_code not in zip_to_respondent:
                zip_to_respondent[zip_code] = []
            zip_to_respondent[zip_code].append(idx)

print(f"Valid 5-digit ZIP codes found: {len(cleaned_zips)}")

# Count ZIP codes
zip_counts = Counter(cleaned_zips)
print(f"\nTop 10 ZIP codes by response count:")
for zip_code, count in zip_counts.most_common(10):
    print(f"  {zip_code}: {count} respondents ({count/len(df)*100:.1f}% of all respondents)")

# District analysis
print(f"\nCITY COUNCIL DISTRICT DATA:")
valid_districts = df[district_col].dropna()
print(f"Respondents who provided district: {len(valid_districts)} ({len(valid_districts)/len(df)*100:.1f}%)")

district_counts = Counter(valid_districts)
print(f"\nResponses by district:")
for district, count in sorted(district_counts.items()):
    print(f"  {district}: {count} respondents ({count/len(df)*100:.1f}% of all respondents)")

# Cross-tabulation: Barriers by ZIP code (for heat map potential)
print("\n" + "=" * 80)
print("BARRIERS BY GEOGRAPHIC AREA (Top 5 ZIP codes)")
print("=" * 80)

# Get top 5 ZIP codes
top_zips = [z[0] for z in zip_counts.most_common(5)]

for zip_code in top_zips:
    zip_barrier_counts = Counter()
    zip_respondent_indices = zip_to_respondent.get(zip_code, [])
    zip_total = len(zip_respondent_indices)
    zip_with_barriers = 0
    
    for idx in zip_respondent_indices:
        if idx < len(df) and pd.notna(df.iloc[idx][barriers_col]):
            response = str(df.iloc[idx][barriers_col])
            if response.strip().lower() not in ['none', 'no barriers', 'n/a', 'na', '']:
                zip_with_barriers += 1
                barriers = [b.strip() for b in response.split(';') if b.strip()]
                for barrier in barriers:
                    if barrier and barrier.lower() not in ['none', 'no barriers', 'n/a', 'na', '']:
                        zip_barrier_counts[barrier] += 1
    
    print(f"\nZIP {zip_code} ({zip_total} total respondents, {zip_with_barriers} with barriers):")
    for barrier, count in zip_barrier_counts.most_common(3):
        percentage = (count / zip_with_barriers) * 100 if zip_with_barriers > 0 else 0
        print(f"  {barrier[:45]}: {count} ({percentage:.1f}% of ZIP respondents with barriers)")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY INSIGHTS")
print("=" * 80)

print("\nKEY FINDINGS:")
print("1. Response Rate: {:.1f}% of survey respondents answered the barriers question".format(
    df[barriers_col].notna().sum()/len(df)*100))

# Get top 3 barriers
top_barriers = barrier_respondent_counts.most_common(3)
print("\n2. Top 3 Barriers by Percentage of Respondents:")
for i, (barrier, count) in enumerate(top_barriers, 1):
    pct_of_barriers = (count / total_respondents_with_barriers) * 100
    pct_of_all = (count / len(df)) * 100
    print(f"   {i}. {barrier}:")
    print(f"      - {count} respondents")
    print(f"      - {pct_of_barriers:.1f}% of those with barriers")
    print(f"      - {pct_of_all:.1f}% of all survey respondents")

print("\n3. Transportation Insights:")
print(f"   - {transport_total} respondents mentioned transportation/parking issues")
print(f"   - This is {transport_total/total_respondents_with_barriers*100:.1f}% of those with barriers")
print(f"   - This is {transport_total/len(df)*100:.1f}% of all survey respondents")

print("\n4. Geographic Coverage:")
print(f"   - {len(zip_counts)} unique ZIP codes represented")
print(f"   - {len(district_counts)} City Council districts represented")
print(f"   - Top ZIP code ({zip_counts.most_common(1)[0][0]}) had {zip_counts.most_common(1)[0][1]} respondents")

# Save results to CSV
results_df = pd.DataFrame([
    {
        'Barrier': barrier,
        'Respondent_Count': count,
        'Percentage_of_Those_With_Barriers': round((count / total_respondents_with_barriers) * 100, 1),
        'Percentage_of_All_Respondents': round((count / len(df)) * 100, 1)
    }
    for barrier, count in barrier_respondent_counts.most_common()
])

results_df.to_csv('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/barrier_analysis_results.csv', index=False)
print("\n5. Results saved to: barrier_analysis_results.csv")

# Create a geographic summary CSV
geo_summary = []
for zip_code, count in zip_counts.most_common(20):  # Top 20 ZIPs
    geo_summary.append({
        'ZIP_Code': zip_code,
        'Total_Respondents': count,
        'Percentage_of_Survey': round((count / len(df)) * 100, 1)
    })

geo_df = pd.DataFrame(geo_summary)
geo_df.to_csv('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/geographic_summary.csv', index=False)
print("6. Geographic summary saved to: geographic_summary.csv")