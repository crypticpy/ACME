"""Question-level analyzer for aggregating and synthesizing response features."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import statistics

from openai import OpenAI, AzureOpenAI
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from rich.progress import track

from ..config import settings
from ..validation.audit import AuditLogger
from ..llm.client import LLMClient
from .models import (
    ResponseFeatures, 
    QuestionAnalysis, 
    QuestionTheme,
    SentimentType,
    StakeholderType,
    UrgencyLevel
)
from .extractor import ResponseFeatureExtractor

console = Console()


class QuestionAnalyzer:
    """
    Analyzes all responses for a specific question to identify patterns and insights.
    
    Implements the question-level aggregation strategy from PROJECT_PLAN.md,
    processing all 10,588 responses organized by question.
    """
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize the question analyzer."""
        self.audit_logger = audit_logger or AuditLogger()
        self.feature_extractor = ResponseFeatureExtractor(audit_logger)
        
        # Set up question analysis cache directory
        self.question_cache_dir = settings.data_dir / "features" / "questions"
        self.question_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize LLM client (handles Azure OpenAI automatically)
        self.llm_client = LLMClient(audit_logger=self.audit_logger)
        self.model = self.llm_client.model
    
    def load_question_responses(self, question_id: str, all_responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Load all responses for a specific question.
        
        Args:
            question_id: The question identifier
            all_responses: All survey responses
            
        Returns:
            List of responses for this question
        """
        question_responses = [
            resp for resp in all_responses 
            if resp.get('question_id') == question_id and resp.get('text', '').strip()
        ]
        
        self.audit_logger.log_operation(
            operation="load_question_responses",
            question_id=question_id,
            response_count=len(question_responses)
        )
        
        return question_responses
    
    def extract_all_features(self, responses: List[Dict[str, Any]], 
                           question_text: str) -> List[ResponseFeatures]:
        """
        Extract features from all responses for a question.
        
        Args:
            responses: List of response dictionaries
            question_text: The full question text
            
        Returns:
            List of ResponseFeatures objects
        """
        console.print(f"\n[bold]Extracting features for {len(responses)} responses...[/bold]")
        
        features_list = []
        
        for response in track(responses, description="Extracting features"):
            features = self.feature_extractor.extract_features(
                response=response['text'],
                question=question_text,
                response_id=response['id'],
                question_id=response['question_id']
            )
            
            if features:
                features_list.append(features)
        
        success_rate = len(features_list) / len(responses) * 100 if responses else 0
        console.print(f"[green]✓[/green] Extracted features from {len(features_list)} responses ({success_rate:.1f}% success rate)")
        
        return features_list
    
    def aggregate_themes(self, features_list: List[ResponseFeatures]) -> List[QuestionTheme]:
        """
        Aggregate themes across all responses for a question.
        
        Args:
            features_list: List of extracted features
            
        Returns:
            List of QuestionTheme objects sorted by frequency
        """
        # Count theme occurrences
        theme_counter = Counter()
        theme_sentiments = defaultdict(lambda: defaultdict(int))
        theme_urgencies = defaultdict(list)
        theme_stakeholders = defaultdict(lambda: defaultdict(int))
        theme_quotes = defaultdict(list)
        
        for features in features_list:
            for theme in features.themes:
                theme_counter[theme] += 1
                theme_sentiments[theme][features.sentiment] += 1
                theme_urgencies[theme].append(features.urgency)
                theme_stakeholders[theme][features.stakeholder_type] += 1
                
                # Collect representative quotes (key phrases)
                for phrase in features.key_phrases:
                    if theme.lower() in phrase.lower():
                        theme_quotes[theme].append(phrase)
        
        # Build QuestionTheme objects
        question_themes = []
        total_responses = len(features_list)
        
        for theme, count in theme_counter.most_common():
            # Calculate urgency score (high=1.0, medium=0.5, low=0.0)
            urgency_scores = {
                UrgencyLevel.high: 1.0,
                UrgencyLevel.medium: 0.5,
                UrgencyLevel.low: 0.0
            }
            avg_urgency = statistics.mean([
                urgency_scores[u] for u in theme_urgencies[theme]
            ])
            
            # Get top representative quotes (limit to 5)
            quotes = list(set(theme_quotes[theme]))[:5]
            
            question_theme = QuestionTheme(
                theme=theme,
                count=count,
                percentage=(count / total_responses * 100) if total_responses > 0 else 0,
                representative_quotes=quotes,
                sentiment_distribution=dict(theme_sentiments[theme]),
                urgency_score=avg_urgency,
                stakeholder_breakdown=dict(theme_stakeholders[theme])
            )
            
            question_themes.append(question_theme)
        
        return question_themes
    
    def identify_contradictions_and_consensus(self, features_list: List[ResponseFeatures],
                                            themes: List[QuestionTheme]) -> Tuple[List[str], List[str]]:
        """
        Identify areas of contradiction and consensus in responses.
        
        Args:
            features_list: List of extracted features
            themes: Aggregated themes
            
        Returns:
            Tuple of (contradictions, consensus_points)
        """
        contradictions = []
        consensus_points = []
        
        # Analyze sentiment distribution for major themes
        for theme in themes[:10]:  # Focus on top 10 themes
            sentiment_dist = theme.sentiment_distribution
            total_mentions = sum(sentiment_dist.values())
            
            if total_mentions < 10:  # Skip themes with too few mentions
                continue
            
            # Calculate sentiment percentages
            positive_pct = sentiment_dist.get(SentimentType.positive, 0) / total_mentions * 100
            negative_pct = sentiment_dist.get(SentimentType.negative, 0) / total_mentions * 100
            
            # Identify contradictions (significant split in sentiment)
            if positive_pct > 30 and negative_pct > 30:
                contradictions.append(
                    f"{theme.theme}: {positive_pct:.0f}% positive vs {negative_pct:.0f}% negative views"
                )
            
            # Identify consensus (overwhelming agreement)
            elif positive_pct > 70:
                consensus_points.append(
                    f"Strong positive consensus on {theme.theme} ({positive_pct:.0f}% positive)"
                )
            elif negative_pct > 70:
                consensus_points.append(
                    f"Strong negative consensus on {theme.theme} ({negative_pct:.0f}% negative)"
                )
        
        return contradictions, consensus_points
    
    def generate_insights_and_recommendations(self, question_text: str, 
                                            themes: List[QuestionTheme],
                                            features_list: List[ResponseFeatures]) -> Tuple[List[str], List[str]]:
        """
        Generate key insights and recommendations using GPT-4.1.
        
        Args:
            question_text: The question being analyzed
            themes: Aggregated themes
            features_list: All extracted features
            
        Returns:
            Tuple of (key_insights, recommendations)
        """
        if not self.llm_client.client or not themes:
            return [], []
        
        # Prepare theme summary for GPT-4.1
        theme_summary = "\n".join([
            f"- {theme.theme}: {theme.count} mentions ({theme.percentage:.1f}%), "
            f"urgency score: {theme.urgency_score:.2f}"
            for theme in themes[:15]  # Top 15 themes
        ])
        
        # Count key statistics
        total_responses = len(features_list)
        high_urgency_count = sum(1 for f in features_list if f.urgency == UrgencyLevel.high)
        actionable_count = sum(1 for f in features_list if f.contains_actionable_feedback)
        
        system_prompt = """You are a senior municipal policy analyst specializing in cultural funding.

## Identity
You synthesize community feedback into actionable insights for city leadership.

## Instructions
Based on the aggregated analysis data, generate:
1. 3-5 key insights that capture the most important findings
2. 3-5 specific, actionable recommendations

Focus on:
- Patterns that affect the most people
- Issues with high urgency scores
- Opportunities for systemic improvement
- Evidence-based solutions

## ACCURACY
Ground all insights and recommendations in the data provided."""

        user_prompt = f"""Question: {question_text}

Total Responses Analyzed: {total_responses}
High Urgency Issues: {high_urgency_count} ({high_urgency_count/total_responses*100:.1f}%)
Actionable Feedback: {actionable_count} ({actionable_count/total_responses*100:.1f}%)

Top Themes:
{theme_summary}

Generate key insights and actionable recommendations based on this analysis."""

        try:
            # Add request for JSON output
            json_prompt = user_prompt + "\n\nReturn a JSON object with keys 'key_insights' (array of insights) and 'recommendations' (array of recommendations)."
            
            # Use LLMClient
            response = self.llm_client.generate_response(
                prompt=json_prompt,
                instructions=system_prompt,
                temperature=0.4
            )
            
            # Parse response
            result = json.loads(response.content)
            
            insights = result.get('key_insights', [])
            recommendations = result.get('recommendations', [])
            
            return insights, recommendations
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="generate_insights",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            return [], []
    
    def analyze_question(self, question_id: str, question_text: str,
                        all_responses: List[Dict[str, Any]]) -> Optional[QuestionAnalysis]:
        """
        Perform complete analysis for a single question.
        
        Args:
            question_id: Unique identifier for the question
            question_text: Full text of the question
            all_responses: All survey responses
            
        Returns:
            QuestionAnalysis object with complete analysis
        """
        # Check if already analyzed
        cache_file = self.question_cache_dir / f"{question_id}_analysis.json"
        if cache_file.exists():
            console.print(f"[dim]Loading cached analysis for question {question_id}[/dim]")
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return QuestionAnalysis(**data)
        
        console.print(f"\n[bold blue]Analyzing Question: {question_id}[/bold blue]")
        console.print(f"[dim]{question_text}[/dim]")
        
        # Load responses for this question
        question_responses = self.load_question_responses(question_id, all_responses)
        
        if not question_responses:
            console.print(f"[yellow]No responses found for question {question_id}[/yellow]")
            return None
        
        # Extract features from all responses
        features_list = self.extract_all_features(question_responses, question_text)
        
        if not features_list:
            console.print(f"[red]Failed to extract features for question {question_id}[/red]")
            return None
        
        # Aggregate themes
        themes = self.aggregate_themes(features_list)
        
        # Calculate distributions
        sentiment_dist = defaultdict(int)
        urgency_dist = defaultdict(int)
        stakeholder_dist = defaultdict(int)
        
        for features in features_list:
            sentiment_dist[features.sentiment] += 1
            urgency_dist[features.urgency] += 1
            stakeholder_dist[features.stakeholder_type] += 1
        
        # Identify contradictions and consensus
        contradictions, consensus = self.identify_contradictions_and_consensus(features_list, themes)
        
        # Generate insights and recommendations
        insights, recommendations = self.generate_insights_and_recommendations(
            question_text, themes, features_list
        )
        
        # Create QuestionAnalysis object
        analysis = QuestionAnalysis(
            question_id=question_id,
            question_text=question_text,
            response_count=len(features_list),
            dominant_themes=themes[:20],  # Top 20 themes
            sentiment_distribution=dict(sentiment_dist),
            urgency_distribution=dict(urgency_dist),
            stakeholder_distribution=dict(stakeholder_dist),
            key_insights=insights,
            recommendations=recommendations,
            contradictions=contradictions,
            consensus_points=consensus
        )
        
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(analysis.model_dump(), f, indent=2)
        
        self.audit_logger.log_operation(
            operation="question_analysis_complete",
            question_id=question_id,
            response_count=analysis.response_count,
            theme_count=len(analysis.dominant_themes),
            cache_file=str(cache_file)
        )
        
        # Display summary
        self._display_analysis_summary(analysis)
        
        return analysis
    
    def _display_analysis_summary(self, analysis: QuestionAnalysis) -> None:
        """Display a summary of the question analysis."""
        console.print(f"\n[bold green]Analysis Complete for {analysis.question_id}[/bold green]")
        
        # Create summary table
        table = Table(title="Analysis Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Responses", str(analysis.response_count))
        table.add_row("Themes Identified", str(len(analysis.dominant_themes)))
        table.add_row("Key Insights", str(len(analysis.key_insights)))
        table.add_row("Recommendations", str(len(analysis.recommendations)))
        
        # Add sentiment breakdown
        sentiment_summary = ", ".join([
            f"{k.value}: {v}" for k, v in analysis.sentiment_distribution.items()
        ])
        table.add_row("Sentiment", sentiment_summary)
        
        # Add urgency breakdown
        urgency_summary = ", ".join([
            f"{k.value}: {v}" for k, v in analysis.urgency_distribution.items()
        ])
        table.add_row("Urgency", urgency_summary)
        
        console.print(table)
        
        # Show top themes
        console.print("\n[bold]Top 5 Themes:[/bold]")
        for i, theme in enumerate(analysis.dominant_themes[:5], 1):
            console.print(f"{i}. {theme.theme} ({theme.count} mentions, {theme.percentage:.1f}%)")
    
    def analyze_all_questions(self, questions: List[Dict[str, str]], 
                            all_responses: List[Dict[str, Any]]) -> List[QuestionAnalysis]:
        """
        Analyze all questions in the survey.
        
        Args:
            questions: List of question dictionaries with 'id' and 'text'
            all_responses: All survey responses
            
        Returns:
            List of QuestionAnalysis objects
        """
        analyses = []
        
        console.print(f"\n[bold]Analyzing {len(questions)} questions...[/bold]")
        
        for question in questions:
            analysis = self.analyze_question(
                question_id=question['id'],
                question_text=question['text'],
                all_responses=all_responses
            )
            
            if analysis:
                analyses.append(analysis)
        
        console.print(f"\n[bold green]✓ Completed analysis for {len(analyses)} questions[/bold green]")
        
        return analyses