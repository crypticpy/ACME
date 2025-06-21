"""Cross-question synthesizer for identifying meta-themes and strategic insights."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import statistics

from openai import OpenAI, AzureOpenAI
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from ..config import settings
from ..validation.audit import AuditLogger
from ..llm.client import LLMClient
from .models import (
    QuestionAnalysis,
    CrossQuestionInsight,
    SentimentType,
    StakeholderType,
    UrgencyLevel
)

console = Console()


class CrossQuestionSynthesizer:
    """
    Synthesizes insights across multiple questions to identify meta-themes and patterns.
    
    Implements the cross-question analysis strategy from PROJECT_PLAN.md,
    finding connections and contradictions across the full survey.
    """
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize the cross-question synthesizer."""
        self.audit_logger = audit_logger or AuditLogger()
        
        # Set up synthesis cache directory
        self.synthesis_cache_dir = settings.data_dir / "features" / "themes"
        self.synthesis_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize LLM client (handles Azure OpenAI automatically)
        self.llm_client = LLMClient(audit_logger=self.audit_logger)
        self.model = self.llm_client.model
    
    def identify_recurring_themes(self, analyses: List[QuestionAnalysis]) -> Dict[str, Dict[str, Any]]:
        """
        Identify themes that appear across multiple questions.
        
        Args:
            analyses: List of QuestionAnalysis objects
            
        Returns:
            Dictionary of recurring themes with metadata
        """
        # Track theme occurrences across questions
        theme_questions = defaultdict(list)  # theme -> list of question_ids
        theme_total_mentions = defaultdict(int)
        theme_urgencies = defaultdict(list)
        theme_sentiments = defaultdict(lambda: defaultdict(int))
        
        for analysis in analyses:
            for theme in analysis.dominant_themes:
                theme_key = self._normalize_theme(theme.theme)
                theme_questions[theme_key].append(analysis.question_id)
                theme_total_mentions[theme_key] += theme.count
                theme_urgencies[theme_key].append(theme.urgency_score)
                
                # Aggregate sentiment
                for sentiment, count in theme.sentiment_distribution.items():
                    theme_sentiments[theme_key][sentiment] += count
        
        # Filter for themes appearing in multiple questions
        recurring_themes = {}
        
        for theme, question_ids in theme_questions.items():
            if len(set(question_ids)) >= 2:  # Appears in at least 2 questions
                avg_urgency = statistics.mean(theme_urgencies[theme])
                
                recurring_themes[theme] = {
                    'theme': theme,
                    'question_count': len(set(question_ids)),
                    'total_mentions': theme_total_mentions[theme],
                    'question_ids': list(set(question_ids)),
                    'average_urgency': avg_urgency,
                    'sentiment_distribution': dict(theme_sentiments[theme])
                }
        
        # Sort by total mentions
        recurring_themes = dict(sorted(
            recurring_themes.items(),
            key=lambda x: x[1]['total_mentions'],
            reverse=True
        ))
        
        self.audit_logger.log_operation(
            operation="identify_recurring_themes",
            recurring_theme_count=len(recurring_themes),
            total_questions_analyzed=len(analyses)
        )
        
        return recurring_themes
    
    def _normalize_theme(self, theme: str) -> str:
        """Normalize theme names for comparison across questions."""
        # Simple normalization - could be enhanced with NLP
        return theme.lower().strip().replace('-', ' ').replace('_', ' ')
    
    def analyze_stakeholder_perspectives(self, analyses: List[QuestionAnalysis]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze how different stakeholder groups respond across questions.
        
        Args:
            analyses: List of QuestionAnalysis objects
            
        Returns:
            Dictionary of stakeholder perspectives
        """
        stakeholder_data = defaultdict(lambda: {
            'response_count': 0,
            'top_themes': Counter(),
            'sentiment_distribution': defaultdict(int),
            'urgency_distribution': defaultdict(int),
            'questions_engaged': set()
        })
        
        for analysis in analyses:
            # Aggregate stakeholder data from each question
            for stakeholder, count in analysis.stakeholder_distribution.items():
                data = stakeholder_data[stakeholder]
                data['response_count'] += count
                data['questions_engaged'].add(analysis.question_id)
                
                # Estimate stakeholder themes (proportional to their representation)
                stakeholder_ratio = count / analysis.response_count if analysis.response_count > 0 else 0
                
                for theme in analysis.dominant_themes[:10]:  # Top 10 themes
                    estimated_mentions = int(theme.count * stakeholder_ratio)
                    if estimated_mentions > 0:
                        data['top_themes'][theme.theme] += estimated_mentions
        
        # Convert to regular dict and process
        stakeholder_perspectives = {}
        
        for stakeholder, data in stakeholder_data.items():
            stakeholder_perspectives[stakeholder.value] = {
                'total_responses': data['response_count'],
                'questions_engaged': len(data['questions_engaged']),
                'top_concerns': [
                    {'theme': theme, 'mentions': count}
                    for theme, count in data['top_themes'].most_common(10)
                ],
                'engagement_rate': len(data['questions_engaged']) / len(analyses) * 100
            }
        
        return stakeholder_perspectives
    
    def identify_systemic_issues(self, recurring_themes: Dict[str, Dict[str, Any]],
                               stakeholder_perspectives: Dict[str, Dict[str, Any]]) -> List[CrossQuestionInsight]:
        """
        Identify systemic issues that span multiple questions and stakeholders.
        
        Args:
            recurring_themes: Dictionary of recurring themes
            stakeholder_perspectives: Dictionary of stakeholder perspectives
            
        Returns:
            List of CrossQuestionInsight objects
        """
        insights = []
        
        # Analyze high-urgency recurring themes
        for theme_data in recurring_themes.values():
            if theme_data['average_urgency'] >= 0.7 and theme_data['question_count'] >= 3:
                
                # Determine affected stakeholders
                affected_stakeholders = []
                for stakeholder, perspective in stakeholder_perspectives.items():
                    if any(concern['theme'].lower() == theme_data['theme'].lower() 
                          for concern in perspective['top_concerns'][:5]):
                        affected_stakeholders.append(StakeholderType(stakeholder))
                
                insight = CrossQuestionInsight(
                    insight_type="recurring_barrier",
                    description=f"{theme_data['theme'].title()} identified as a persistent barrier across {theme_data['question_count']} questions",
                    supporting_questions=theme_data['question_ids'][:5],  # Limit to 5
                    evidence_count=theme_data['total_mentions'],
                    confidence=min(0.9, theme_data['average_urgency'] + 0.2),  # Cap at 0.9
                    implications=[
                        f"Affects {len(affected_stakeholders)} stakeholder groups",
                        f"Mentioned {theme_data['total_mentions']} times across survey",
                        f"Requires coordinated policy response"
                    ],
                    affected_stakeholders=affected_stakeholders,
                    severity_score=theme_data['average_urgency']
                )
                
                insights.append(insight)
        
        return insights
    
    def analyze_sentiment_patterns(self, analyses: List[QuestionAnalysis]) -> Dict[str, Any]:
        """
        Analyze sentiment patterns across questions.
        
        Args:
            analyses: List of QuestionAnalysis objects
            
        Returns:
            Dictionary of sentiment patterns
        """
        # Aggregate sentiment data
        overall_sentiment = defaultdict(int)
        question_sentiments = {}
        
        for analysis in analyses:
            question_sentiments[analysis.question_id] = analysis.sentiment_distribution
            
            for sentiment, count in analysis.sentiment_distribution.items():
                overall_sentiment[sentiment] += count
        
        # Calculate percentages
        total_responses = sum(overall_sentiment.values())
        sentiment_percentages = {
            sentiment.value: (count / total_responses * 100) if total_responses > 0 else 0
            for sentiment, count in overall_sentiment.items()
        }
        
        # Identify questions with notably different sentiment
        outlier_questions = []
        overall_negative_pct = sentiment_percentages.get('negative', 0)
        
        for analysis in analyses:
            question_total = sum(analysis.sentiment_distribution.values())
            if question_total > 0:
                question_negative_pct = (
                    analysis.sentiment_distribution.get(SentimentType.negative, 0) / question_total * 100
                )
                
                # Flag if significantly more negative than average
                if question_negative_pct > overall_negative_pct + 20:
                    outlier_questions.append({
                        'question_id': analysis.question_id,
                        'question_text': analysis.question_text[:100] + '...',
                        'negative_percentage': question_negative_pct,
                        'difference': question_negative_pct - overall_negative_pct
                    })
        
        return {
            'overall_sentiment': sentiment_percentages,
            'total_responses_analyzed': total_responses,
            'outlier_questions': sorted(outlier_questions, key=lambda x: x['difference'], reverse=True)
        }
    
    def generate_strategic_insights(self, analyses: List[QuestionAnalysis],
                                  recurring_themes: Dict[str, Dict[str, Any]],
                                  systemic_issues: List[CrossQuestionInsight]) -> List[str]:
        """
        Generate strategic insights using GPT-4.1 synthesis.
        
        Args:
            analyses: List of QuestionAnalysis objects
            recurring_themes: Dictionary of recurring themes
            systemic_issues: List of identified systemic issues
            
        Returns:
            List of strategic insights
        """
        if not self.llm_client.client or not analyses:
            return []
        
        # Prepare summary data
        total_responses = sum(a.response_count for a in analyses)
        top_themes = list(recurring_themes.items())[:10]
        
        theme_summary = "\n".join([
            f"- {data['theme']}: {data['total_mentions']} mentions across "
            f"{data['question_count']} questions (urgency: {data['average_urgency']:.2f})"
            for _, data in top_themes
        ])
        
        systemic_summary = "\n".join([
            f"- {issue.description} (confidence: {issue.confidence:.2f})"
            for issue in systemic_issues[:5]
        ])
        
        system_prompt = """You are a strategic advisor to Austin's cultural affairs leadership.

## Identity
You synthesize complex community feedback into actionable strategic guidance.

## Instructions
Based on the cross-question analysis, generate 5-7 strategic insights that:
1. Connect patterns across multiple areas of concern
2. Identify root causes rather than symptoms
3. Suggest systemic interventions
4. Consider equity and access implications
5. Provide clear direction for policy development

## ACCURACY
All insights must be grounded in the analysis data provided."""

        user_prompt = f"""Cross-Question Analysis Summary:

Total Survey Responses: {total_responses}
Questions Analyzed: {len(analyses)}

Top Recurring Themes:
{theme_summary}

Identified Systemic Issues:
{systemic_summary}

Generate strategic insights that address these cross-cutting concerns."""

        try:
            # Add request for JSON output
            json_prompt = user_prompt + "\n\nReturn a JSON object with key 'strategic_insights' containing an array of strategic insights."
            
            # Use LLMClient
            response = self.llm_client.generate_response(
                prompt=json_prompt,
                instructions=system_prompt,
                temperature=0.4
            )
            
            result = json.loads(response.content)
            return result.get('strategic_insights', [])
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="generate_strategic_insights",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            return []
    
    def synthesize_insights(self, analyses: List[QuestionAnalysis]) -> Dict[str, Any]:
        """
        Perform complete cross-question synthesis.
        
        Args:
            analyses: List of QuestionAnalysis objects from all questions
            
        Returns:
            Dictionary containing all synthesis results
        """
        console.print("\n[bold blue]Performing Cross-Question Synthesis...[/bold blue]")
        
        # Check cache
        cache_file = self.synthesis_cache_dir / "cross_question_synthesis.json"
        if cache_file.exists():
            console.print("[dim]Loading cached synthesis results[/dim]")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        with console.status("[bold green]Analyzing patterns across questions...") as status:
            
            # 1. Identify recurring themes
            status.update("Identifying recurring themes...")
            recurring_themes = self.identify_recurring_themes(analyses)
            console.print(f"[green]✓[/green] Found {len(recurring_themes)} recurring themes")
            
            # 2. Analyze stakeholder perspectives
            status.update("Analyzing stakeholder perspectives...")
            stakeholder_perspectives = self.analyze_stakeholder_perspectives(analyses)
            console.print(f"[green]✓[/green] Analyzed {len(stakeholder_perspectives)} stakeholder groups")
            
            # 3. Identify systemic issues
            status.update("Identifying systemic issues...")
            systemic_issues = self.identify_systemic_issues(recurring_themes, stakeholder_perspectives)
            console.print(f"[green]✓[/green] Identified {len(systemic_issues)} systemic issues")
            
            # 4. Analyze sentiment patterns
            status.update("Analyzing sentiment patterns...")
            sentiment_patterns = self.analyze_sentiment_patterns(analyses)
            console.print(f"[green]✓[/green] Sentiment analysis complete")
            
            # 5. Generate strategic insights
            status.update("Generating strategic insights...")
            strategic_insights = self.generate_strategic_insights(
                analyses, recurring_themes, systemic_issues
            )
            console.print(f"[green]✓[/green] Generated {len(strategic_insights)} strategic insights")
        
        # Compile results
        synthesis_results = {
            'metadata': {
                'synthesis_date': datetime.now().isoformat(),
                'questions_analyzed': len(analyses),
                'total_responses': sum(a.response_count for a in analyses)
            },
            'recurring_themes': recurring_themes,
            'stakeholder_perspectives': stakeholder_perspectives,
            'systemic_issues': [issue.model_dump() for issue in systemic_issues],
            'sentiment_patterns': sentiment_patterns,
            'strategic_insights': strategic_insights
        }
        
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(synthesis_results, f, indent=2)
        
        self.audit_logger.log_operation(
            operation="cross_question_synthesis_complete",
            recurring_themes=len(recurring_themes),
            systemic_issues=len(systemic_issues),
            strategic_insights=len(strategic_insights),
            cache_file=str(cache_file)
        )
        
        # Display summary
        self._display_synthesis_summary(synthesis_results)
        
        return synthesis_results
    
    def _display_synthesis_summary(self, results: Dict[str, Any]) -> None:
        """Display a summary of the synthesis results."""
        console.print("\n[bold green]Cross-Question Synthesis Complete[/bold green]")
        
        # Create summary table
        table = Table(title="Synthesis Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="white")
        
        table.add_row("Recurring Themes", str(len(results['recurring_themes'])))
        table.add_row("Systemic Issues", str(len(results['systemic_issues'])))
        table.add_row("Strategic Insights", str(len(results['strategic_insights'])))
        table.add_row("Questions Analyzed", str(results['metadata']['questions_analyzed']))
        table.add_row("Total Responses", str(results['metadata']['total_responses']))
        
        console.print(table)
        
        # Show top recurring themes
        console.print("\n[bold]Top 5 Recurring Themes:[/bold]")
        for i, (theme, data) in enumerate(list(results['recurring_themes'].items())[:5], 1):
            console.print(
                f"{i}. {theme} - {data['total_mentions']} mentions across "
                f"{data['question_count']} questions"
            )