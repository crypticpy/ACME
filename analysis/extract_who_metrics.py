#!/usr/bin/env python3
"""Extract WHO quantitative metrics from NEW_Data Excel files."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

def extract_survey_metrics():
    """Extract quantitative metrics from ACME Community Survey."""
    
    # Load the survey data
    survey_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Community_Survey.xlsx")
    df = pd.read_excel(survey_path)
    
    print(f"Total survey responses: {len(df)}")
    
    # Extract participant roles/relationships
    role_column = None
    for col in df.columns:
        if 'role' in col.lower() and 'relationship' in col.lower():
            role_column = col
            break
    
    if role_column:
        print(f"\nAnalyzing roles from column: {role_column}")
        
        # Parse multi-select responses
        all_roles = []
        role_counts = {}
        
        for idx, response in enumerate(df[role_column].dropna()):
            if pd.isna(response):
                continue
                
            # Split by common delimiters
            roles = str(response).split(';')
            for role in roles:
                role = role.strip()
                if role:
                    all_roles.append(role)
                    role_counts[role] = role_counts.get(role, 0) + 1
        
        # Categorize into requested groups
        creatives_keywords = ['artist', 'musician', 'performer', 'creative', 'maker', 'designer', 'writer']
        org_keywords = ['organization', 'nonprofit', 'staff', 'administrator', 'director', 'manager']
        patron_keywords = ['patron', 'audience', 'community member', 'resident', 'attendee', 'visitor']
        
        creatives_count = 0
        org_staff_count = 0
        patrons_count = 0
        
        # Count unique respondents in each category
        for idx, response in enumerate(df[role_column].dropna()):
            if pd.isna(response):
                continue
            
            response_lower = str(response).lower()
            is_creative = any(keyword in response_lower for keyword in creatives_keywords)
            is_org = any(keyword in response_lower for keyword in org_keywords)
            is_patron = any(keyword in response_lower for keyword in patron_keywords)
            
            if is_creative:
                creatives_count += 1
            if is_org:
                org_staff_count += 1
            if is_patron:
                patrons_count += 1
        
        # Calculate Share of Voice
        total_categorized = creatives_count + org_staff_count + patrons_count
        
        who_metrics = {
            "survey_responses": len(df),
            "focus_groups": 0,  # To be filled from Working Document
            "one_on_ones": 0,   # To be filled from Working Document
            "listening_sessions": "Not available",
            "share_of_voice": {
                "creatives": {
                    "count": creatives_count,
                    "percentage": round((creatives_count / len(df)) * 100, 1) if len(df) > 0 else 0
                },
                "organizational_staff": {
                    "count": org_staff_count,
                    "percentage": round((org_staff_count / len(df)) * 100, 1) if len(df) > 0 else 0
                },
                "community_patrons": {
                    "count": patrons_count,
                    "percentage": round((patrons_count / len(df)) * 100, 1) if len(df) > 0 else 0
                }
            },
            "all_roles_breakdown": role_counts,
            "total_respondents": len(df),
            "extraction_date": datetime.now().isoformat()
        }
        
        # Print summary
        print("\n=== WHO METRICS SUMMARY ===")
        print(f"Total Survey Responses: {who_metrics['survey_responses']}")
        print(f"\nShare of Voice:")
        print(f"- Creatives: {who_metrics['share_of_voice']['creatives']['count']} ({who_metrics['share_of_voice']['creatives']['percentage']}%)")
        print(f"- Organizational Staff: {who_metrics['share_of_voice']['organizational_staff']['count']} ({who_metrics['share_of_voice']['organizational_staff']['percentage']}%)")
        print(f"- Community Members/Patrons: {who_metrics['share_of_voice']['community_patrons']['count']} ({who_metrics['share_of_voice']['community_patrons']['percentage']}%)")
        
        print(f"\nTop 10 Role Responses:")
        sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for role, count in sorted_roles:
            print(f"  - {role}: {count}")
        
        return who_metrics
    else:
        print("Could not find role/relationship column")
        return None

def check_working_document():
    """Check Working Document for focus group and 1:1 data."""
    
    working_doc_path = Path("/Users/aiml/Downloads/ACME2/NEW_Data/ACME_Working_Document.xlsx")
    
    # Load all sheets
    all_sheets = pd.read_excel(working_doc_path, sheet_name=None)
    
    print("\n=== WORKING DOCUMENT ANALYSIS ===")
    print(f"Sheets found: {list(all_sheets.keys())}")
    
    focus_group_count = 0
    one_on_one_count = 0
    
    # Check each sheet for focus group or 1:1 indicators
    for sheet_name, df in all_sheets.items():
        print(f"\nAnalyzing sheet: {sheet_name}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)[:5]}...")  # First 5 columns
        
        # Look for focus group or 1:1 indicators in column names or data
        for col in df.columns:
            col_lower = str(col).lower()
            if 'focus' in col_lower and 'group' in col_lower:
                non_empty = df[col].dropna()
                if len(non_empty) > 0:
                    print(f"  Found focus group data in column: {col}")
                    focus_group_count += len(non_empty)
            elif '1:1' in col_lower or 'one on one' in col_lower or 'interview' in col_lower:
                non_empty = df[col].dropna()
                if len(non_empty) > 0:
                    print(f"  Found 1:1 interview data in column: {col}")
                    one_on_one_count += len(non_empty)
        
        # Also check for indicators in the data itself
        if sheet_name.lower() in ['database', 'data']:
            # Look for method/type columns
            for col in df.columns:
                if 'method' in str(col).lower() or 'type' in str(col).lower():
                    value_counts = df[col].value_counts()
                    print(f"\n  Data collection methods in {col}:")
                    for method, count in value_counts.items():
                        print(f"    - {method}: {count}")
                        if 'focus' in str(method).lower():
                            focus_group_count = max(focus_group_count, count)
                        elif '1:1' in str(method).lower() or 'interview' in str(method).lower():
                            one_on_one_count = max(one_on_one_count, count)
    
    return focus_group_count, one_on_one_count

def save_who_metrics():
    """Extract and save all WHO metrics."""
    
    # Extract survey metrics
    who_metrics = extract_survey_metrics()
    
    if who_metrics:
        # Check for focus groups and 1:1s
        focus_groups, one_on_ones = check_working_document()
        
        # Update metrics
        who_metrics['focus_groups'] = focus_groups
        who_metrics['one_on_ones'] = one_on_ones
        
        # Save to file
        output_path = Path("data/results/who_metrics.json")
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_path, 'w') as f:
            json.dump(who_metrics, f, indent=2)
        
        print(f"\n✓ WHO metrics saved to: {output_path}")
        
        # Also save a formatted summary
        summary_path = Path("data/results/WHO_ANALYSIS_SUMMARY.md")
        
        summary = f"""# WHO: Quantitative Analysis

**Generated:** {datetime.now().strftime('%B %d, %Y')}

## Data Collection Methods

- **Survey Responses:** {who_metrics['survey_responses']:,}
- **Focus Groups:** {who_metrics['focus_groups']}
- **1:1 Interviews:** {who_metrics['one_on_ones']}
- **Listening Sessions:** {who_metrics['listening_sessions']}

## Share of Voice

| Participant Type | Count | Percentage |
|-----------------|-------|------------|
| Creatives | {who_metrics['share_of_voice']['creatives']['count']:,} | {who_metrics['share_of_voice']['creatives']['percentage']}% |
| Organizational Staff | {who_metrics['share_of_voice']['organizational_staff']['count']:,} | {who_metrics['share_of_voice']['organizational_staff']['percentage']}% |
| Community Members/Patrons | {who_metrics['share_of_voice']['community_patrons']['count']:,} | {who_metrics['share_of_voice']['community_patrons']['percentage']}% |

## Notes

- Total unique respondents: {who_metrics['total_respondents']:,}
- Some respondents may belong to multiple categories
- Percentages based on total survey responses
"""
        
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print(f"✓ WHO summary saved to: {summary_path}")

if __name__ == "__main__":
    save_who_metrics()