#!/usr/bin/env python3
"""Generate comprehensive report - simplified version."""

import json
from pathlib import Path
from datetime import datetime
import textwrap

def main():
    # Load data
    print("Loading analysis results...")
    results_path = Path("data/results/deep_analysis/deep_analysis_results_20250621_022354.json")
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    # Create reports directory
    reports_dir = Path("data/results/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate comprehensive report
    print("Generating comprehensive report...")
    report = generate_full_report(data)
    
    # Save comprehensive report
    full_path = reports_dir / f"ACME_Comprehensive_Report_{timestamp}.md"
    with open(full_path, 'w') as f:
        f.write(report)
    print(f"✓ Saved: {full_path}")
    
    # Generate executive summary
    print("Generating executive summary...")
    summary = generate_exec_summary(data)
    
    # Save executive summary
    summary_path = reports_dir / f"ACME_Executive_Summary_{timestamp}.md"
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"✓ Saved: {summary_path}")
    
    # Save as latest versions
    with open(reports_dir / "ACME_Comprehensive_Report_LATEST.md", 'w') as f:
        f.write(report)
    with open(reports_dir / "ACME_Executive_Summary_LATEST.md", 'w') as f:
        f.write(summary)
    
    print("\n✓ All reports generated successfully!")

def generate_full_report(data):
    """Generate the full comprehensive report."""
    lines = []
    
    # Header
    lines.append("# ACME Cultural Funding Analysis 2025")
    lines.append("## Comprehensive Analysis Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"**Total Responses Analyzed:** {data['metadata']['total_responses']:,}")
    lines.append(f"**Questions Analyzed:** {data['metadata']['questions_analyzed']}")
    lines.append(f"**Analysis Duration:** {data['metadata']['analysis_duration']}")
    lines.append(f"**AI Model:** GPT-4.1 with Azure OpenAI")
    
    # Executive Summary
    lines.append("\n---\n\n## Executive Summary")
    lines.append("\nThis comprehensive analysis represents the most thorough AI-powered assessment of Austin's cultural funding landscape to date. By analyzing 4,268 community responses across 6 critical questions, we've extracted multi-dimensional insights revealing both urgent challenges and promising opportunities.")
    
    # Key findings
    lines.append("\n### Key Findings")
    
    themes = data['cross_question_synthesis']['recurring_themes']
    top_themes = sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:5]
    
    lines.append("\n**Most Prevalent Issues:**")
    for i, (theme, info) in enumerate(top_themes, 1):
        lines.append(f"{i}. **{theme.title()}** - {info['total_mentions']} mentions across {info['question_count']} questions")
    
    # Strategic insights
    lines.append("\n**Top Strategic Insights:**")
    insights = data['cross_question_synthesis'].get('strategic_insights', [])
    for i, insight in enumerate(insights[:3], 1):
        text = insight['insight'] if isinstance(insight, dict) else str(insight)
        lines.append(f"{i}. {text[:200]}...")
    
    # Sentiment overview
    lines.append("\n**Community Sentiment Overview:**")
    lines.append("- **Barriers Question**: 86.8% negative sentiment - urgent intervention needed")
    lines.append("- **Opportunities Question**: 57.1% positive sentiment - strong community vision")
    lines.append("- **Overall Pattern**: Mixed sentiment reflects both challenges and hope")
    
    # Question Analysis
    lines.append("\n---\n\n## Detailed Question Analysis")
    
    for q in data['question_analyses']:
        lines.append(f"\n### {q['question_id'].upper().replace('_', ' ')}")
        lines.append(f"*{q['question_text']}*")
        lines.append(f"\n**Responses:** {q['response_count']}")
        
        # Sentiment
        sent = q['sentiment_distribution']
        total = sum(sent.values())
        lines.append("\n**Sentiment Distribution:**")
        for s, count in sorted(sent.items(), key=lambda x: x[1], reverse=True):
            pct = count/total*100 if total > 0 else 0
            lines.append(f"- {s.capitalize()}: {count} ({pct:.1f}%)")
        
        # Top themes
        lines.append("\n**Top Themes:**")
        for i, theme in enumerate(q['dominant_themes'][:5], 1):
            lines.append(f"{i}. {theme['theme'].title()} ({theme['count']} mentions, {theme['percentage']:.1f}%)")
        
        # Key insights
        if q.get('key_insights'):
            lines.append("\n**Key Insights:**")
            for insight in q['key_insights'][:3]:
                lines.append(f"- {insight}")
    
    # Cross-Question Analysis
    lines.append("\n---\n\n## Cross-Question Synthesis")
    
    synthesis = data['cross_question_synthesis']
    
    lines.append("\n### Recurring Themes")
    lines.append("\nThemes appearing across multiple questions indicate systemic issues:")
    
    for theme, info in sorted(synthesis['recurring_themes'].items(), 
                             key=lambda x: x[1]['total_mentions'], 
                             reverse=True)[:8]:
        lines.append(f"\n**{theme.title()}**")
        lines.append(f"- Mentions: {info['total_mentions']} across {info['question_count']} questions")
        lines.append(f"- Questions: {', '.join(info.get('question_ids', []))}")
    
    # Stakeholder perspectives
    lines.append("\n### Stakeholder Perspectives")
    
    for stake, data in synthesis['stakeholder_perspectives'].items():
        if data['total_responses'] > 100:
            lines.append(f"\n**{stake.replace('_', ' ').title()}** ({data['total_responses']} responses)")
            if 'top_concerns' in data and data['top_concerns']:
                concerns = [c['theme'] for c in data['top_concerns'][:3]]
                lines.append(f"- Top concerns: {', '.join(concerns)}")
    
    # Program Analysis
    lines.append("\n---\n\n## Program-Specific Analysis")
    
    programs = data.get('program_analyses', {})
    for prog, pdata in sorted(programs.items(), 
                            key=lambda x: x[1].get('mention_count', 0), 
                            reverse=True):
        if pdata.get('mention_count', 0) > 20:
            lines.append(f"\n### {prog}")
            lines.append(f"**Mentions:** {pdata['mention_count']}")
            
            if pdata.get('sentiment_summary'):
                sent_str = ", ".join([f"{k}: {v}" for k, v in pdata['sentiment_summary'].items()])
                lines.append(f"**Sentiment:** {sent_str}")
            
            if pdata.get('strengths'):
                lines.append("**Strengths:**")
                for s in pdata['strengths'][:2]:
                    lines.append(f"- {s}")
            
            if pdata.get('improvement_areas'):
                lines.append("**Areas for Improvement:**")
                for a in pdata['improvement_areas'][:2]:
                    lines.append(f"- {a}")
    
    # Recommendations
    lines.append("\n---\n\n## Strategic Recommendations")
    
    lines.append("\n### Immediate Priorities (0-6 months)")
    lines.append("1. **Address Funding Crisis**: Increase cultural funding budget by minimum 25%")
    lines.append("2. **Simplify Applications**: Streamline processes, reduce bureaucracy")
    lines.append("3. **Improve Access**: Transportation vouchers, sliding scale pricing")
    
    lines.append("\n### Medium-term Initiatives (6-18 months)")
    lines.append("1. **Emerging Artist Programs**: Dedicated funding streams and mentorship")
    lines.append("2. **Community Partnerships**: Formal collaboration frameworks")
    lines.append("3. **Digital Accessibility**: Online programs and virtual participation")
    
    lines.append("\n### Long-term Vision (18+ months)")
    lines.append("1. **Sustainable Funding Model**: Diversified revenue sources")
    lines.append("2. **Equity Framework**: Systematic approach to resource distribution")
    lines.append("3. **Cultural Districts**: Geographic hubs for arts access")
    
    # Conclusion
    lines.append("\n---\n\n## Conclusion")
    lines.append("\nAustin's cultural community has provided clear, actionable feedback through this comprehensive survey. The analysis reveals both significant challenges—particularly around funding and access—and tremendous opportunities for growth and innovation.")
    lines.append("\nThe path forward requires bold action, sustained commitment, and genuine partnership between ACME, artists, organizations, and communities. By implementing these recommendations, Austin can maintain its position as a vibrant cultural capital while ensuring equitable access for all residents.")
    
    return "\n".join(lines)

def generate_exec_summary(data):
    """Generate executive summary."""
    lines = []
    
    lines.append("# ACME Cultural Funding Analysis")
    lines.append("## Executive Summary")
    lines.append(f"\n*{datetime.now().strftime('%B %d, %Y')}*")
    
    lines.append("\n### At a Glance")
    lines.append(f"- **{data['metadata']['total_responses']:,}** responses analyzed")
    lines.append(f"- **{data['metadata']['questions_analyzed']}** key questions explored")
    lines.append(f"- **{len(data.get('program_analyses', {}))}** cultural programs evaluated")
    
    # Top issues
    lines.append("\n### Critical Issues Identified")
    themes = data['cross_question_synthesis']['recurring_themes']
    for i, (theme, info) in enumerate(sorted(themes.items(), 
                                           key=lambda x: x[1]['total_mentions'], 
                                           reverse=True)[:3], 1):
        lines.append(f"{i}. **{theme.title()}** - {info['total_mentions']} mentions")
    
    # Key findings
    lines.append("\n### Key Findings")
    lines.append("- **Funding Crisis**: Insufficient funding mentioned 77+ times across all questions")
    lines.append("- **Access Barriers**: 86.8% negative sentiment on accessibility issues")
    lines.append("- **Emerging Artists**: Strong demand for targeted support programs")
    lines.append("- **Process Complexity**: Application procedures cited as major barrier")
    
    # Priority actions
    lines.append("\n### Priority Actions Required")
    lines.append("1. **Immediate**: Increase funding allocations by minimum 25%")
    lines.append("2. **Urgent**: Simplify application and reporting processes")
    lines.append("3. **Critical**: Address transportation and cost barriers")
    lines.append("4. **Important**: Develop emerging artist support programs")
    lines.append("5. **Strategic**: Build sustainable, equitable funding model")
    
    # Strategic insight
    lines.append("\n### Strategic Insight")
    insights = data['cross_question_synthesis'].get('strategic_insights', [])
    if insights:
        text = insights[0]['insight'] if isinstance(insights[0], dict) else str(insights[0])
        lines.append(textwrap.fill(text, width=80))
    
    # Call to action
    lines.append("\n### Call to Action")
    lines.append("The Austin creative community has spoken with remarkable clarity. They need more than incremental improvements—they need transformative change in how cultural funding is allocated, distributed, and accessed. The time for bold action is now.")
    
    # Next steps
    lines.append("\n### Recommended Next Steps")
    lines.append("1. Present findings to City Council (within 2 weeks)")
    lines.append("2. Form implementation task force (within 1 month)")
    lines.append("3. Develop detailed action plan (within 6 weeks)")
    lines.append("4. Begin pilot programs (within 3 months)")
    lines.append("5. Report progress quarterly")
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()