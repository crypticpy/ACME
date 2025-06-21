import pandas as pd
import numpy as np
from collections import Counter
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Read the Excel file
file_path = '/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx'
df = pd.read_excel(file_path)

# Get the barriers column
barriers_col = 'What barriers, if any, prevent you from participating in arts and culture events in Austin? (Select all that apply.)'

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

for response in df[barriers_col].dropna():
    if pd.isna(response) or response == 'None' or response == 'No barriers':
        continue
    
    total_respondents_with_barriers += 1
    
    # Split by semicolon and clean
    barriers = [b.strip() for b in str(response).split(';') if b.strip()]
    
    # Count each unique barrier per respondent (only once per respondent)
    unique_barriers = set(barriers)
    for barrier in unique_barriers:
        barrier_respondent_counts[barrier] += 1
        
        # Track transportation subcategories
        if 'Transportation / parking' in barrier:
            transportation_details['Transportation/Parking (General)'] += 1
        elif 'parking' in barrier.lower():
            transportation_details['Parking Specific'] += 1
        elif 'transit' in barrier.lower() or 'bus' in barrier.lower() or 'public transport' in barrier.lower():
            transportation_details['Public Transit'] += 1

# Calculate percentages
print(f"\nTotal respondents who identified at least one barrier: {total_respondents_with_barriers}")

print("\nBARRIER THEMES BY PERCENTAGE OF RESPONDENTS:")
print("-" * 60)
print(f"{'Barrier':<50} {'Count':<10} {'Percentage':<10}")
print("-" * 60)

# Sort by count and display
for barrier, count in barrier_respondent_counts.most_common():
    percentage = (count / total_respondents_with_barriers) * 100
    print(f"{barrier[:50]:<50} {count:<10} {percentage:.1f}%")

# Transportation breakdown
print("\n" + "=" * 80)
print("TRANSPORTATION BARRIER BREAKDOWN")
print("=" * 80)
print(f"\nOf the respondents who mentioned transportation barriers:")
for transport_type, count in transportation_details.most_common():
    percentage = (count / total_respondents_with_barriers) * 100
    print(f"  {transport_type}: {count} respondents ({percentage:.1f}% of all respondents)")

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
for z in valid_zips:
    # Extract 5-digit ZIP codes
    zip_match = re.search(r'\b\d{5}\b', str(z))
    if zip_match:
        cleaned_zips.append(zip_match.group())

print(f"Valid 5-digit ZIP codes found: {len(cleaned_zips)}")

# Count ZIP codes
zip_counts = Counter(cleaned_zips)
print(f"\nTop 10 ZIP codes by response count:")
for zip_code, count in zip_counts.most_common(10):
    print(f"  {zip_code}: {count} respondents")

# District analysis
print(f"\nCITY COUNCIL DISTRICT DATA:")
valid_districts = df[district_col].dropna()
print(f"Respondents who provided district: {len(valid_districts)} ({len(valid_districts)/len(df)*100:.1f}%)")

district_counts = Counter(valid_districts)
print(f"\nResponses by district:")
for district, count in sorted(district_counts.items()):
    print(f"  {district}: {count} respondents")

# Cross-tabulation: Barriers by ZIP code (for heat map potential)
print("\n" + "=" * 80)
print("BARRIERS BY GEOGRAPHIC AREA (Top 5 ZIP codes)")
print("=" * 80)

# Create a dataframe for geographic analysis
geo_barrier_data = []
for idx, row in df.iterrows():
    if pd.notna(row[barriers_col]) and pd.notna(row[zip_col]):
        zip_match = re.search(r'\b\d{5}\b', str(row[zip_col]))
        if zip_match:
            zip_code = zip_match.group()
            barriers = [b.strip() for b in str(row[barriers_col]).split(';') if b.strip()]
            for barrier in barriers:
                geo_barrier_data.append({
                    'zip': zip_code,
                    'barrier': barrier
                })

if geo_barrier_data:
    geo_df = pd.DataFrame(geo_barrier_data)
    
    # Get top 5 ZIP codes
    top_zips = [z[0] for z in zip_counts.most_common(5)]
    
    for zip_code in top_zips:
        zip_barriers = geo_df[geo_df['zip'] == zip_code]['barrier'].value_counts()
        zip_total = zip_counts[zip_code]
        
        print(f"\nZIP {zip_code} ({zip_total} respondents):")
        for barrier, count in zip_barriers.head(3).items():
            if barrier:  # Skip empty strings
                percentage = (count / zip_total) * 100
                print(f"  {barrier[:40]}: {percentage:.1f}% of ZIP respondents")

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
    percentage = (count / total_respondents_with_barriers) * 100
    print(f"   {i}. {barrier}: {percentage:.1f}%")

print("\n3. Transportation Insights:")
total_transport = sum(1 for response in df[barriers_col].dropna() 
                     if 'Transportation' in str(response) or 'parking' in str(response).lower())
print(f"   - {total_transport} respondents ({total_transport/total_respondents_with_barriers*100:.1f}%) mentioned transportation/parking issues")

print("\n4. Geographic Coverage:")
print(f"   - {len(zip_counts)} unique ZIP codes represented")
print(f"   - {len(district_counts)} City Council districts represented")

# Save results to CSV
results_df = pd.DataFrame([
    {
        'Barrier': barrier,
        'Respondent_Count': count,
        'Percentage_of_Respondents': round((count / total_respondents_with_barriers) * 100, 1)
    }
    for barrier, count in barrier_respondent_counts.most_common()
])

results_df.to_csv('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/barrier_analysis_results.csv', index=False)
print("\n5. Results saved to: barrier_analysis_results.csv")