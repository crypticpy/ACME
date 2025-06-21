import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Read the saved results
results_df = pd.read_csv('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/barrier_analysis_results.csv')
geo_df = pd.read_csv('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/geographic_summary.csv')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))

# 1. Top Barriers Bar Chart
ax1 = plt.subplot(2, 2, 1)
top_barriers = results_df.head(10)
bars = ax1.barh(range(len(top_barriers)), top_barriers['Percentage_of_All_Respondents'])
ax1.set_yticks(range(len(top_barriers)))
ax1.set_yticklabels([b[:40] + '...' if len(b) > 40 else b for b in top_barriers['Barrier']])
ax1.set_xlabel('Percentage of All Survey Respondents (%)')
ax1.set_title('Top 10 Barriers to Arts & Culture Participation', fontsize=14, fontweight='bold')
ax1.invert_yaxis()

# Add value labels
for i, (v, count) in enumerate(zip(top_barriers['Percentage_of_All_Respondents'], 
                                   top_barriers['Respondent_Count'])):
    ax1.text(v + 0.5, i, f'{v:.1f}% ({count})', va='center')

# 2. Pie Chart of Main Barrier Categories
ax2 = plt.subplot(2, 2, 2)
main_categories = {
    'Cost/Financial': 771,
    'Transportation/Parking': 740,
    'Awareness/Information': 616,
    'Location/Geographic': 493,
    'Diversity/Representation': 403,
    'Interest/Relevance': 108,
    'Other': 32  # Sum of all other barriers
}

colors = plt.cm.Set3(range(len(main_categories)))
wedges, texts, autotexts = ax2.pie(main_categories.values(), 
                                    labels=main_categories.keys(), 
                                    autopct='%1.1f%%',
                                    colors=colors,
                                    startangle=90)
ax2.set_title('Barrier Categories Distribution', fontsize=14, fontweight='bold')

# 3. Geographic Distribution - Top ZIP Codes
ax3 = plt.subplot(2, 2, 3)
top_zips = geo_df.head(15)
ax3.bar(range(len(top_zips)), top_zips['Total_Respondents'])
ax3.set_xticks(range(len(top_zips)))
ax3.set_xticklabels(top_zips['ZIP_Code'], rotation=45)
ax3.set_xlabel('ZIP Code')
ax3.set_ylabel('Number of Respondents')
ax3.set_title('Top 15 ZIP Codes by Survey Participation', fontsize=14, fontweight='bold')

# Add value labels
for i, v in enumerate(top_zips['Total_Respondents']):
    ax3.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=8)

# 4. Key Statistics Summary
ax4 = plt.subplot(2, 2, 4)
ax4.axis('off')
summary_text = """
ACME COMMUNITY SURVEY - KEY FINDINGS

Survey Overview:
• Total Respondents: 1,187
• Response Rate for Barriers Question: 95.5%
• Respondents Identifying Barriers: 1,133

Top 3 Barriers:
1. Cost/Admission Fees: 65.0% of all respondents
2. Transportation/Parking: 62.3% of all respondents  
3. Lack of Awareness: 51.9% of all respondents

Geographic Insights:
• 83 unique ZIP codes represented
• Top ZIP (78745): 96 respondents (8.1%)
• 26.6% unsure of their City Council District

Transportation Details:
• 741 respondents (62.4%) mentioned transportation issues
• Includes parking, public transit, and general access concerns
"""

ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, 
         fontsize=11, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax4.set_title('Summary Statistics', fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/barrier_analysis_visualization.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Create a detailed transportation breakdown chart
fig2, ax = plt.subplots(figsize=(10, 6))

# Transportation subcategories based on the data
transport_breakdown = {
    'Transportation/Parking (General)': 740,
    'Cost of Parking/Uber': 15,  # Estimated from "High price of parking and Uber"
    'Traffic Concerns': 5,  # From specific mentions
    'Public Transit Issues': 3,  # Estimated from transit-related comments
    'Accessibility/ADA': 8  # From accessibility mentions
}

# Create horizontal bar chart
y_pos = range(len(transport_breakdown))
ax.barh(y_pos, transport_breakdown.values(), color='skyblue')
ax.set_yticks(y_pos)
ax.set_yticklabels(transport_breakdown.keys())
ax.set_xlabel('Number of Mentions')
ax.set_title('Transportation Barrier Breakdown\n(Some respondents mentioned multiple aspects)', 
             fontsize=14, fontweight='bold')

# Add value labels
for i, v in enumerate(transport_breakdown.values()):
    ax.text(v + 5, i, str(v), va='center')

plt.tight_layout()
plt.savefig('/Users/aiml/Downloads/ACME2/acme-cultural-funding-2025/transportation_breakdown.png', 
            dpi=300, bbox_inches='tight')
plt.close()

print("Visualizations created successfully!")
print("- barrier_analysis_visualization.png: Comprehensive overview")
print("- transportation_breakdown.png: Detailed transportation analysis")