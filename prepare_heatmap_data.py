import pandas as pd
import numpy as np
from collections import Counter
import re
import json

# Read the Excel file
file_path = '/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx'
df = pd.read_excel(file_path)

# Find the barriers column
barriers_col = None
for col in df.columns:
    if 'barriers' in col.lower() and 'prevent' in col.lower():
        barriers_col = col
        break

zip_col = 'What zip code do you reside in?'

# Create detailed geographic analysis for heat map
print("PREPARING HEAT MAP DATA")
print("=" * 60)

# Dictionary to store barrier data by ZIP
zip_barrier_data = {}

# Process each response
for idx, row in df.iterrows():
    if pd.notna(row[barriers_col]) and pd.notna(row[zip_col]):
        # Extract ZIP code
        zip_match = re.search(r'\b\d{5}\b', str(row[zip_col]))
        if zip_match:
            zip_code = zip_match.group()
            
            # Initialize ZIP entry if needed
            if zip_code not in zip_barrier_data:
                zip_barrier_data[zip_code] = {
                    'total_respondents': 0,
                    'respondents_with_barriers': 0,
                    'cost_barriers': 0,
                    'transportation_barriers': 0,
                    'awareness_barriers': 0,
                    'location_barriers': 0,
                    'diversity_barriers': 0,
                    'all_barriers': []
                }
            
            zip_barrier_data[zip_code]['total_respondents'] += 1
            
            # Check if they have barriers
            response_str = str(row[barriers_col]).strip()
            if response_str.lower() not in ['none', 'no barriers', 'n/a', 'na', '']:
                zip_barrier_data[zip_code]['respondents_with_barriers'] += 1
                
                # Split barriers
                barriers = [b.strip() for b in response_str.split(';') if b.strip()]
                zip_barrier_data[zip_code]['all_barriers'].extend(barriers)
                
                # Categorize barriers
                for barrier in barriers:
                    barrier_lower = barrier.lower()
                    if 'cost' in barrier_lower or 'ticket' in barrier_lower or 'admission' in barrier_lower:
                        zip_barrier_data[zip_code]['cost_barriers'] += 1
                    if 'transport' in barrier_lower or 'parking' in barrier_lower:
                        zip_barrier_data[zip_code]['transportation_barriers'] += 1
                    if 'awareness' in barrier_lower or 'information' in barrier_lower:
                        zip_barrier_data[zip_code]['awareness_barriers'] += 1
                    if 'location' in barrier_lower or 'nearby' in barrier_lower or 'neighborhood' in barrier_lower:
                        zip_barrier_data[zip_code]['location_barriers'] += 1
                    if 'diversity' in barrier_lower or 'representation' in barrier_lower or 'inclusion' in barrier_lower:
                        zip_barrier_data[zip_code]['diversity_barriers'] += 1

# Create summary dataframe for heat map
heatmap_data = []
for zip_code, data in zip_barrier_data.items():
    if data['total_respondents'] >= 5:  # Only include ZIPs with at least 5 respondents
        row = {
            'zip_code': zip_code,
            'total_respondents': data['total_respondents'],
            'pct_with_barriers': (data['respondents_with_barriers'] / data['total_respondents'] * 100) if data['total_respondents'] > 0 else 0,
            'pct_cost': (data['cost_barriers'] / data['total_respondents'] * 100) if data['total_respondents'] > 0 else 0,
            'pct_transportation': (data['transportation_barriers'] / data['total_respondents'] * 100) if data['total_respondents'] > 0 else 0,
            'pct_awareness': (data['awareness_barriers'] / data['total_respondents'] * 100) if data['total_respondents'] > 0 else 0,
            'pct_location': (data['location_barriers'] / data['total_respondents'] * 100) if data['total_respondents'] > 0 else 0,
            'pct_diversity': (data['diversity_barriers'] / data['total_respondents'] * 100) if data['total_respondents'] > 0 else 0,
            'barrier_intensity': len(data['all_barriers']) / data['total_respondents'] if data['total_respondents'] > 0 else 0
        }
        heatmap_data.append(row)

# Create dataframe and save
heatmap_df = pd.DataFrame(heatmap_data)
heatmap_df = heatmap_df.sort_values('total_respondents', ascending=False)

# Save to CSV
heatmap_df.to_csv('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/heatmap_data.csv', index=False)

# Print summary
print(f"\nHeat map data prepared for {len(heatmap_df)} ZIP codes")
print(f"(Included only ZIPs with 5+ respondents)")

print("\nTop 10 ZIPs by barrier intensity (avg barriers per respondent):")
top_intensity = heatmap_df.nlargest(10, 'barrier_intensity')
for _, row in top_intensity.iterrows():
    print(f"  {row['zip_code']}: {row['barrier_intensity']:.2f} barriers/respondent ({row['total_respondents']} respondents)")

print("\nTop 10 ZIPs by transportation barrier percentage:")
top_transport = heatmap_df.nlargest(10, 'pct_transportation')
for _, row in top_transport.iterrows():
    print(f"  {row['zip_code']}: {row['pct_transportation']:.1f}% ({row['total_respondents']} respondents)")

# Create JSON for potential web mapping
geojson_features = []
for _, row in heatmap_df.iterrows():
    feature = {
        "type": "Feature",
        "properties": {
            "zip": row['zip_code'],
            "respondents": int(row['total_respondents']),
            "pct_barriers": round(row['pct_with_barriers'], 1),
            "pct_cost": round(row['pct_cost'], 1),
            "pct_transport": round(row['pct_transportation'], 1),
            "pct_awareness": round(row['pct_awareness'], 1),
            "intensity": round(row['barrier_intensity'], 2)
        }
    }
    geojson_features.append(feature)

# Save JSON
with open('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/barrier_heatmap_data.json', 'w') as f:
    json.dump({
        "type": "FeatureCollection",
        "features": geojson_features
    }, f, indent=2)

print("\nFiles created:")
print("- heatmap_data.csv: ZIP-level barrier statistics")
print("- barrier_heatmap_data.json: GeoJSON-ready data for web mapping")

# Austin ZIP code coordinates (sample - would need full list for actual mapping)
austin_zip_coords = {
    "78701": {"lat": 30.2672, "lon": -97.7431},  # Downtown
    "78702": {"lat": 30.2606, "lon": -97.7147},  # East Austin
    "78703": {"lat": 30.2874, "lon": -97.7576},  # Central/West
    "78704": {"lat": 30.2428, "lon": -97.7703},  # South Austin
    "78745": {"lat": 30.1900, "lon": -97.7956},  # South Austin
    "78723": {"lat": 30.3042, "lon": -97.6830},  # Northeast
    "78751": {"lat": 30.3102, "lon": -97.7250},  # Hyde Park
    "78748": {"lat": 30.1688, "lon": -97.8235},  # Southwest
    "78741": {"lat": 30.2302, "lon": -97.6895},  # Southeast
    "78721": {"lat": 30.2701, "lon": -97.6884},  # East
}

print("\nNote: For actual heat map visualization, you would need:")
print("1. Complete ZIP code boundary data (shapefiles)")
print("2. GIS software or web mapping library (Leaflet, Mapbox, etc.)")
print("3. The prepared data files above can be imported into these tools")