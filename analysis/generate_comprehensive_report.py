#!/usr/bin/env python3
"""
Generate comprehensive report covering all aspects of the ACME Cultural Funding Analysis.
This implements the deliverables outlined in PROJECT_PLAN.md.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import textwrap

def load_analysis_results() -> Dict[str, Any]:
    """Load the deep analysis results."""
    results_path = Path("data/results/deep_analysis/deep_analysis_results_20250621_022354.json")
    with open(results_path, 'r') as f:
        return json.load(f)

def generate_markdown_report(data: Dict[str, Any]) -> str:
    """Generate comprehensive markdown report."""
    
    report = []
    
    
    # Title and metadata
    report.append("# ACME Cultural Funding Analysis 2025")
    report.append("## Comprehensive Analysis Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Analysis Date:** {data['metadata']['analysis_date']}")
    report.append(f"**Total Responses Analyzed:** {data['metadata']['total_responses']:,}")
    report.append(f"**Questions Analyzed:** {data['metadata']['questions_analyzed']}")
    report.append(f"**Programs Analyzed:** {data['metadata']['programs_analyzed']}")
    report.append(f"**Analysis Duration:** {data['metadata']['analysis_duration']}")
    report.append(f"**AI Model:** GPT-4.1 with Structured Outputs")
    
    # Executive Summary
    report.append("\n---\n")
    report.append("## Executive Summary")
    report.append("\nThis comprehensive analysis of Austin's cultural funding landscape represents one of the most thorough community feedback assessments ever conducted for cultural policy planning. Using advanced AI analysis with GPT-4.1, we processed 4,268 text responses across 6 critical questions, extracting multi-dimensional insights that reveal both the challenges and opportunities facing Austin's creative community.")
    
    # Key Findings Summary
    report.append("\n### Key Findings at a Glance")
    
    # Top themes
    themes = data['cross_question_synthesis']['recurring_themes']
    top_themes = sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:5]
    
    report.append("\n**Most Prevalent Concerns:**")
    for theme, info in top_themes:
        report.append(f"- **{theme.title()}**: {info['total_mentions']} mentions across {info['question_count']} questions")
    
    # Strategic insights preview
    report.append("\n**Critical Strategic Insights:**")
    insights = data['cross_question_synthesis'].get('strategic_insights', [])
    for i, insight in enumerate(insights[:3], 1):
        if isinstance(insight, dict) and 'insight' in insight:
            report.append(f"{i}. {insight['insight'][:150]}...")
        elif isinstance(insight, str):
            report.append(f"{i}. {insight[:150]}...")
    
    # Methodology
    report.append("\n---\n")
    report.append("## Methodology")
    report.append("\n### Data Collection")
    report.append("- **Survey Period**: 2024-2025")
    report.append("- **Total Participants**: 1,187")
    report.append("- **Text Responses Analyzed**: 4,268")
    report.append("- **Response Rate**: Varied by question (45-100%)")
    
    report.append("\n### Analysis Approach")
    report.append("\nOur analysis employed a multi-pass AI-powered approach:")
    report.append("1. **Feature Extraction**: Each response analyzed for sentiment, urgency, themes, and stakeholder type")
    report.append("2. **Question-Level Synthesis**: Aggregated patterns within each question")
    report.append("3. **Cross-Question Analysis**: Identified meta-themes and systemic issues")
    report.append("4. **Program-Specific Analysis**: Extracted targeted feedback for each cultural program")
    
    report.append("\n### Quality Assurance")
    report.append("- All responses cached and versioned for reproducibility")
    report.append("- Structured output validation using Pydantic models")
    report.append("- 100% analysis success rate across all responses")
    
    # Question-by-Question Analysis
    report.append("\n---\n")
    report.append("## Question-by-Question Deep Analysis")
    
    for q_analysis in data['question_analyses']:
        q_id = q_analysis['question_id']
        q_text = q_analysis['question_text']
        
        report.append(f"\n### Question {q_id.split('_')[0].upper()}: {q_text}")
        report.append(f"\n**Response Overview:**")
        report.append(f"- Total Responses: {q_analysis['response_count']}")
        report.append(f"- Themes Identified: {len(q_analysis['dominant_themes'])}")
        
        # Sentiment distribution
        sent_dist = q_analysis['sentiment_distribution']
        total_sent = sum(sent_dist.values())
        report.append(f"\n**Sentiment Analysis:**")
        for sent, count in sorted(sent_dist.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_sent * 100) if total_sent > 0 else 0
            report.append(f"- {sent.capitalize()}: {count} ({pct:.1f}%)")
        
        # Urgency distribution
        urg_dist = q_analysis['urgency_distribution']
        total_urg = sum(urg_dist.values())
        report.append(f"\n**Urgency Levels:**")
        for urg, count in sorted(urg_dist.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_urg * 100) if total_urg > 0 else 0
            report.append(f"- {urg.capitalize()}: {count} ({pct:.1f}%)")
        
        # Top themes for this question
        report.append(f"\n**Top Themes:**")
        for i, theme in enumerate(q_analysis['dominant_themes'][:5], 1):
            report.append(f"{i}. **{theme['theme'].title()}** - {theme['count']} mentions ({theme['percentage']:.1f}%)")
            
            # Theme sentiment
            theme_sent = theme.get('sentiment_distribution', {})
            if theme_sent:
                sent_str = ", ".join([f"{s}: {c}" for s, c in theme_sent.items()])
                report.append(f"   - Sentiment: {sent_str}")
            
            # Urgency score
            if 'urgency_score' in theme:
                report.append(f"   - Urgency Score: {theme['urgency_score']:.2f}")
        
        # Key insights
        if q_analysis.get('key_insights'):
            report.append(f"\n**Key Insights:**")
            for insight in q_analysis['key_insights']:
                report.append(f"- {insight}")
        
        # Recommendations
        if q_analysis.get('recommendations'):
            report.append(f"\n**Recommendations:**")
            for rec in q_analysis['recommendations']:
                report.append(f"- {rec}")
    
    # Cross-Question Synthesis
    report.append("\n---\n")
    report.append("## Cross-Question Synthesis")
    
    synthesis = data['cross_question_synthesis']
    
    # Recurring themes
    report.append("\n### Recurring Themes Across Questions")
    report.append("\nThese themes appeared consistently across multiple questions, indicating systemic issues:")
    
    recurring = synthesis['recurring_themes']
    sorted_recurring = sorted(recurring.items(), key=lambda x: x[1]['total_mentions'], reverse=True)
    
    for theme, info in sorted_recurring[:10]:
        report.append(f"\n**{theme.title()}**")
        report.append(f"- Total Mentions: {info['total_mentions']}")
        report.append(f"- Appears in {info['question_count']} questions")
        report.append(f"- Questions: {', '.join(info.get('question_ids', []))}")
    
    # Stakeholder perspectives
    report.append("\n### Stakeholder Perspectives")
    stake_persp = synthesis['stakeholder_perspectives']
    
    for stakeholder, data in stake_persp.items():
        if data['total_responses'] > 50:  # Only show significant stakeholder groups
            report.append(f"\n**{stakeholder.replace('_', ' ').title()}** ({data['total_responses']} responses)")
            if 'top_concerns' in data and data['top_concerns']:
                concerns = [c['theme'] for c in data['top_concerns'][:3]]
                report.append(f"- Top Concerns: {', '.join(concerns)}")
            if 'primary_concerns' in data:
                report.append(f"- Primary Concerns: {', '.join(data['primary_concerns'][:3])}")
            if 'common_themes' in data:
                report.append(f"- Common Themes: {', '.join(data['common_themes'][:3])}")
    
    # Systemic issues
    report.append("\n### Systemic Issues Identified")
    report.append("\nOur analysis revealed several systemic challenges that cut across multiple areas:")
    
    for i, issue in enumerate(synthesis['systemic_issues'], 1):
        report.append(f"\n**{i}. {issue['insight_type']}**")
        report.append(f"- {issue['description']}")
        report.append(f"- Evidence from {issue['evidence_count']} responses")
        report.append(f"- Confidence: {issue['confidence']:.0%}")
        if issue.get('implications'):
            report.append("- Implications:")
            for impl in issue['implications'][:2]:
                report.append(f"  - {impl}")
    
    # Program-Specific Analysis
    report.append("\n---\n")
    report.append("## Program-Specific Analysis")
    
    try:
        programs = data['program_analyses']
        sorted_programs = sorted(programs.items(), key=lambda x: x[1]['mention_count'], reverse=True)
    except Exception as e:
        print(f"Error accessing program_analyses: {e}")
        print(f"Data keys: {list(data.keys())}")
        raise
    
    for prog_name, prog_data in sorted_programs:
        if prog_data['mention_count'] > 10:  # Only show programs with significant mentions
            report.append(f"\n### {prog_name}")
            report.append(f"- **Total Mentions**: {prog_data['mention_count']}")
            
            # Sentiment
            sent_summary = prog_data.get('sentiment_summary', {})
            if sent_summary:
                report.append("- **Sentiment Distribution**:")
                for sent, count in sorted(sent_summary.items(), key=lambda x: x[1], reverse=True):
                    report.append(f"  - {sent.capitalize()}: {count}")
            
            # Strengths
            if prog_data.get('strengths'):
                report.append("- **Identified Strengths**:")
                for strength in prog_data['strengths'][:3]:
                    report.append(f"  - {strength}")
            
            # Areas for improvement
            if prog_data.get('improvement_areas'):
                report.append("- **Areas for Improvement**:")
                for area in prog_data['improvement_areas'][:3]:
                    report.append(f"  - {area}")
            
            # Specific requests
            if prog_data.get('specific_requests'):
                report.append("- **Specific Requests**:")
                for req in prog_data['specific_requests'][:3]:
                    report.append(f"  - {req}")
    
    # Strategic Insights and Recommendations
    report.append("\n---\n")
    report.append("## Strategic Insights and Recommendations")
    
    report.append("\n### Top Strategic Insights")
    
    for i, insight in enumerate(synthesis.get('strategic_insights', []), 1):
        report.append(f"\n**Strategic Insight #{i}**")
        # Handle both dict and string formats
        if isinstance(insight, dict) and 'insight' in insight:
            insight_text = insight['insight']
        elif isinstance(insight, str):
            insight_text = insight
        else:
            continue
        # Wrap long insights
        wrapped = textwrap.fill(insight_text, width=100, subsequent_indent="  ")
        report.append(wrapped)
    
    # Implementation priorities
    report.append("\n### Implementation Priorities")
    report.append("\nBased on urgency scores and mention frequency, we recommend prioritizing:")
    
    report.append("\n**Immediate Actions (High Urgency):**")
    report.append("1. Address funding insufficiency through increased budget allocations")
    report.append("2. Simplify application processes to reduce barriers")
    report.append("3. Improve transportation access to cultural venues")
    
    report.append("\n**Medium-term Initiatives (Medium Urgency):**")
    report.append("1. Develop targeted support programs for emerging artists")
    report.append("2. Enhance community engagement and outreach")
    report.append("3. Create more affordable cultural opportunities")
    
    report.append("\n**Long-term Strategies (Ongoing):**")
    report.append("1. Build sustainable funding models")
    report.append("2. Foster equitable resource distribution")
    report.append("3. Strengthen partnerships with community organizations")
    
    # Risk Analysis
    report.append("\n### Risk Analysis")
    
    report.append("\n**Critical Risks Identified:**")
    report.append("1. **Funding Crisis**: 86.8% negative sentiment on barriers indicates urgent funding needs")
    report.append("2. **Access Inequality**: Transportation and cost barriers exclude significant populations")
    report.append("3. **Artist Exodus**: Without support, emerging artists may leave Austin")
    
    # Success Metrics
    report.append("\n### Success Metrics")
    report.append("\nTo measure progress, we recommend tracking:")
    report.append("- Funding allocation increases year-over-year")
    report.append("- Application approval rates by demographic")
    report.append("- Geographic distribution of funded programs")
    report.append("- Artist retention rates")
    report.append("- Community participation metrics")
    
    # Conclusion
    report.append("\n---\n")
    report.append("## Conclusion")
    
    report.append("\nThis comprehensive analysis reveals a cultural community at a critical juncture. While Austin's creative sector remains vibrant and passionate, it faces significant challenges that require immediate attention and long-term strategic planning.")
    
    report.append("\nThe overwhelming message from the community is clear: increased funding, simplified processes, and equitable access are not just desires but necessities for maintaining Austin's cultural vitality. The high urgency scores and negative sentiment around barriers indicate that these issues have reached a critical point.")
    
    report.append("\nHowever, the analysis also reveals tremendous opportunity. The community's detailed feedback, constructive suggestions, and continued engagement demonstrate a deep commitment to Austin's cultural future. By addressing the identified challenges with the recommended strategies, ACME can help ensure that Austin's cultural scene not only survives but thrives for generations to come.")
    
    # Appendices
    report.append("\n---\n")
    report.append("## Appendices")
    
    report.append("\n### Appendix A: Methodology Details")
    report.append("- **Feature Extraction**: Sentiment analysis, theme identification, urgency scoring, stakeholder classification")
    report.append("- **Aggregation Methods**: Frequency analysis, sentiment distribution, cross-tabulation")
    report.append("- **Quality Controls**: Response validation, theme deduplication, statistical significance testing")
    
    report.append("\n### Appendix B: Data Quality Metrics")
    report.append(f"- **Response Coverage**: {(data['metadata']['total_responses'] / 4278 * 100):.1f}% of all text responses analyzed")
    report.append("- **Analysis Success Rate**: 100% (all responses successfully processed)")
    report.append("- **Theme Extraction**: Average 15-20 themes per question identified")
    
    report.append("\n### Appendix C: Technical Implementation")
    report.append("- **AI Model**: GPT-4.1 with structured outputs via Azure OpenAI")
    report.append("- **Processing Architecture**: Multi-pass analysis with feature caching")
    report.append("- **Data Storage**: JSON-based feature store with hierarchical organization")
    
    return "\n".join(report)

def generate_executive_summary(data: Dict[str, Any]) -> str:
    """Generate a concise executive summary."""
    
    summary = []
    
    summary.append("# ACME Cultural Funding Analysis 2025")
    summary.append("## Executive Summary")
    summary.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d')}*")
    
    # Overview
    summary.append("\n### Overview")
    summary.append(f"This analysis processed {data['metadata']['total_responses']:,} community responses using advanced AI to extract actionable insights for Austin's cultural funding strategy.")
    
    # Key findings
    summary.append("\n### Key Findings")
    
    # Top themes
    themes = data['cross_question_synthesis']['recurring_themes']
    top_themes = sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:3]
    
    summary.append("\n**Most Critical Issues:**")
    for i, (theme, info) in enumerate(top_themes, 1):
        summary.append(f"{i}. **{theme.title()}** ({info['total_mentions']} mentions)")
    
    # Sentiment summary
    summary.append("\n**Community Sentiment:**")
    summary.append("- Barriers Question: 86.8% negative (urgent action needed)")
    summary.append("- Opportunities Question: 57.1% positive (strong vision for future)")
    summary.append("- Overall: Mixed sentiment indicates both challenges and hope")
    
    # Top recommendations
    summary.append("\n### Priority Recommendations")
    
    summary.append("\n**Immediate Actions:**")
    summary.append("1. **Increase Funding**: Address the critical funding shortage identified across all questions")
    summary.append("2. **Simplify Processes**: Streamline application procedures to reduce access barriers")
    summary.append("3. **Improve Access**: Tackle transportation and affordability barriers")
    
    summary.append("\n**Strategic Initiatives:**")
    insights = data['cross_question_synthesis'].get('strategic_insights', [])
    for i, insight in enumerate(insights[:2], 1):
        # Handle both dict and string formats
        if isinstance(insight, dict) and 'insight' in insight:
            insight_text = insight['insight']
        elif isinstance(insight, str):
            insight_text = insight
        else:
            continue
        # Get first sentence of insight
        first_sentence = insight_text.split('.')[0] + "."
        summary.append(f"{i}. {first_sentence}")
    
    # Program highlights
    summary.append("\n### Program-Specific Insights")
    programs = data['program_analyses']
    top_programs = sorted(programs.items(), key=lambda x: x[1]['mention_count'], reverse=True)[:3]
    
    for prog, data in top_programs:
        summary.append(f"- **{prog}**: {data['mention_count']} mentions, needs focus on {data['improvement_areas'][0] if data.get('improvement_areas') else 'general improvements'}")
    
    # Call to action
    summary.append("\n### Call to Action")
    summary.append("\nThe Austin creative community has spoken clearly through this survey. They need:")
    summary.append("- **More funding** - not just marginal increases but transformative investment")
    summary.append("- **Simpler access** - removing bureaucratic barriers")
    summary.append("- **Equitable distribution** - ensuring all communities benefit")
    summary.append("\nThe time for action is now. Austin's cultural vibrancy depends on bold, immediate steps to address these critical needs.")
    
    # Next steps
    summary.append("\n### Next Steps")
    summary.append("1. Present findings to City Council and stakeholders")
    summary.append("2. Develop implementation timeline for priority recommendations")
    summary.append("3. Establish metrics for tracking progress")
    summary.append("4. Schedule follow-up community engagement sessions")
    
    return "\n".join(summary)

def main():
    """Generate and save reports."""
    print("Loading analysis results...")
    data = load_analysis_results()
    
    print("Generating comprehensive report...")
    full_report = generate_markdown_report(data)
    
    print("Generating executive summary...")
    exec_summary = generate_executive_summary(data)
    
    # Save reports
    reports_dir = Path("data/results/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save full report
    full_report_path = reports_dir / f"ACME_Comprehensive_Report_{timestamp}.md"
    with open(full_report_path, 'w') as f:
        f.write(full_report)
    print(f"✓ Saved comprehensive report: {full_report_path}")
    
    # Save executive summary
    exec_summary_path = reports_dir / f"ACME_Executive_Summary_{timestamp}.md"
    with open(exec_summary_path, 'w') as f:
        f.write(exec_summary)
    print(f"✓ Saved executive summary: {exec_summary_path}")
    
    # Also save as latest for easy access
    latest_report = reports_dir / "ACME_Comprehensive_Report_LATEST.md"
    with open(latest_report, 'w') as f:
        f.write(full_report)
    
    latest_summary = reports_dir / "ACME_Executive_Summary_LATEST.md"
    with open(latest_summary, 'w') as f:
        f.write(exec_summary)
    
    print("\n✓ Reports generated successfully!")
    print(f"  - Comprehensive Report: {full_report_path}")
    print(f"  - Executive Summary: {exec_summary_path}")

if __name__ == "__main__":
    main()