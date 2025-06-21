#!/usr/bin/env python3
"""Extract transportation-related comments as a separate 'Parking Lot' item."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

def extract_transportation_comments():
    """Extract all transportation-related comments from survey data."""
    
    print("=== TRANSPORTATION COMMENTS EXTRACTION ===\n")
    
    # Load survey data
    survey_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx")
    df = pd.read_excel(survey_path)
    
    # Transportation keywords
    transportation_keywords = [
        'transport', 'parking', 'bus', 'transit', 'traffic', 'commute', 
        'drive', 'driving', 'car', 'uber', 'lyft', 'ride', 'access',
        'distance', 'location', 'venue location', 'get to', 'getting there',
        'travel', 'metro', 'rail', 'bike', 'walk', 'pedestrian'
    ]
    
    # Store all transportation-related comments
    transportation_comments = []
    comment_categories = Counter()
    
    # Search all text columns
    text_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    for col in text_columns:
        for idx, response in enumerate(df[col].dropna()):
            response_str = str(response)
            response_lower = response_str.lower()
            
            # Check if transportation-related
            is_transportation = any(keyword in response_lower for keyword in transportation_keywords)
            
            if is_transportation:
                # Categorize the type of transportation issue
                categories = []
                
                if any(word in response_lower for word in ['parking', 'park']):
                    categories.append('Parking')
                if any(word in response_lower for word in ['bus', 'transit', 'metro', 'rail', 'public transport']):
                    categories.append('Public Transit')
                if any(word in response_lower for word in ['distance', 'far', 'location', 'venue location']):
                    categories.append('Distance/Location')
                if any(word in response_lower for word in ['cost', 'expensive', 'afford', 'uber', 'lyft']):
                    categories.append('Cost of Transportation')
                if any(word in response_lower for word in ['traffic', 'congestion']):
                    categories.append('Traffic')
                if any(word in response_lower for word in ['bike', 'walk', 'pedestrian']):
                    categories.append('Alternative Transportation')
                
                if not categories:
                    categories = ['General Transportation']
                
                for category in categories:
                    comment_categories[category] += 1
                
                transportation_comments.append({
                    'response_id': idx,
                    'column': col,
                    'comment': response_str,
                    'categories': categories
                })
    
    # Analyze themes within transportation comments
    print(f"Found {len(transportation_comments)} transportation-related comments\n")
    
    # Brief analysis
    analysis = {
        "total_transportation_comments": len(transportation_comments),
        "percentage_of_total_responses": round((len(transportation_comments) / len(df)) * 100, 1),
        "category_breakdown": dict(comment_categories.most_common()),
        "sample_comments": [],
        "key_insights": [],
        "extraction_date": datetime.now().isoformat()
    }
    
    # Get diverse sample comments
    seen_types = set()
    for comment in transportation_comments[:50]:  # Look through first 50
        comment_type = tuple(comment['categories'])
        if comment_type not in seen_types and len(analysis['sample_comments']) < 10:
            seen_types.add(comment_type)
            analysis['sample_comments'].append({
                'categories': comment['categories'],
                'comment': comment['comment'][:300]  # First 300 chars
            })
    
    # Generate insights
    if comment_categories['Parking'] > 20:
        analysis['key_insights'].append(f"Parking is a major concern, mentioned in {comment_categories['Parking']} comments")
    if comment_categories['Public Transit'] > 15:
        analysis['key_insights'].append(f"Public transit access issues mentioned in {comment_categories['Public Transit']} comments")
    if comment_categories['Distance/Location'] > 15:
        analysis['key_insights'].append(f"Distance and venue location challenges noted in {comment_categories['Distance/Location']} comments")
    if comment_categories['Cost of Transportation'] > 10:
        analysis['key_insights'].append(f"Transportation costs are a barrier, mentioned in {comment_categories['Cost of Transportation']} comments")
    
    # Save results
    output_dir = Path("data/results/cultural_funding_analysis")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save JSON
    with open(output_dir / "transportation_parking_lot.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Create markdown report
    md_content = f"""# Transportation Comments - Parking Lot Item

**Generated:** {datetime.now().strftime('%B %d, %Y')}

## Overview

Transportation-related comments have been separated for later analysis as requested.

- **Total Transportation Comments:** {analysis['total_transportation_comments']}
- **Percentage of All Responses:** {analysis['percentage_of_total_responses']}%

## Category Breakdown

| Category | Count |
|----------|-------|
"""
    
    for category, count in comment_categories.most_common():
        md_content += f"| {category} | {count} |\n"
    
    md_content += "\n## Key Insights\n\n"
    for insight in analysis['key_insights']:
        md_content += f"- {insight}\n"
    
    md_content += "\n## Sample Comments\n\n"
    for i, sample in enumerate(analysis['sample_comments'], 1):
        md_content += f"### {i}. {', '.join(sample['categories'])}\n"
        md_content += f"> {sample['comment']}\n\n"
    
    md_content += """
## Recommendation

Transportation and parking issues represent a significant barrier to arts and cultural participation in Austin. 
This topic warrants a separate, focused analysis to develop targeted solutions such as:

- Partnerships with transit agencies for event-specific services
- Venue selection criteria that considers accessibility
- Transportation subsidies or vouchers for cultural events
- Improved information about parking and transit options
"""
    
    with open(output_dir / "TRANSPORTATION_PARKING_LOT.md", 'w') as f:
        f.write(md_content)
    
    # Print summary
    print("=== TRANSPORTATION ANALYSIS SUMMARY ===")
    print(f"\nTotal Comments: {analysis['total_transportation_comments']}")
    print(f"Percentage of Responses: {analysis['percentage_of_total_responses']}%")
    print("\nTop Categories:")
    for category, count in comment_categories.most_common(5):
        print(f"  - {category}: {count}")
    
    print(f"\n✓ Transportation analysis complete! Results saved to: {output_dir}")
    print("  - transportation_parking_lot.json")
    print("  - TRANSPORTATION_PARKING_LOT.md")

if __name__ == "__main__":
    extract_transportation_comments()