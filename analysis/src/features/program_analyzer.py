"""Program-specific analyzer for extracting targeted feedback on cultural programs."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict, Counter
from datetime import datetime

from openai import OpenAI, AzureOpenAI
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from rich.progress import track

from ..config import settings
from ..validation.audit import AuditLogger
from ..llm.client import LLMClient
from .models import (
    ProgramFeedback,
    ResponseFeatures,
    SentimentType,
    StakeholderType
)
from .extractor import ResponseFeatureExtractor

console = Console()


class ProgramAnalyzer:
    """
    Analyzes program-specific feedback from survey responses.
    
    Implements the program analysis strategy from PROJECT_PLAN.md,
    extracting targeted insights for each cultural funding program.
    """
    
    # Known cultural programs to analyze
    CULTURAL_PROGRAMS = [
        "Nexus",
        "Thrive", 
        "Elevate",
        "Austin Live Music Fund",
        "Art in Public Places",
        "Creative Space Assistance Program",
        "Cultural Arts Division",
        "Economic Development Department"
    ]
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize the program analyzer."""
        self.audit_logger = audit_logger or AuditLogger()
        self.feature_extractor = ResponseFeatureExtractor(audit_logger)
        
        # Set up program analysis cache directory
        self.program_cache_dir = settings.data_dir / "features" / "programs"
        self.program_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize LLM client (handles Azure OpenAI automatically)
        self.llm_client = LLMClient(audit_logger=self.audit_logger)
        self.model = self.llm_client.model
        
        # Create program name variations for matching
        self._create_program_patterns()
    
    def _create_program_patterns(self) -> None:
        """Create regex patterns for program name matching."""
        self.program_patterns = {}
        
        for program in self.CULTURAL_PROGRAMS:
            # Create pattern that matches various forms of the program name
            # Handle acronyms, partial matches, and common variations
            pattern_parts = []
            
            # Full name
            pattern_parts.append(re.escape(program))
            
            # Acronym (if multi-word)
            words = program.split()
            if len(words) > 1:
                acronym = ''.join(w[0].upper() for w in words if w[0].isupper())
                if acronym:
                    pattern_parts.append(acronym)
            
            # Common variations
            if "Assistance" in program:
                pattern_parts.append(program.replace("Assistance", "Assist"))
            if "Program" in program:
                pattern_parts.append(program.replace("Program", ""))
            
            # Create case-insensitive pattern
            pattern = r'\b(' + '|'.join(pattern_parts) + r')\b'
            self.program_patterns[program] = re.compile(pattern, re.IGNORECASE)
    
    def identify_program_mentions(self, response_text: str) -> List[str]:
        """
        Identify which programs are mentioned in a response.
        
        Args:
            response_text: The survey response text
            
        Returns:
            List of program names mentioned
        """
        mentioned_programs = []
        
        for program, pattern in self.program_patterns.items():
            if pattern.search(response_text):
                mentioned_programs.append(program)
        
        return mentioned_programs
    
    def extract_program_specific_feedback(self, program_name: str, 
                                        responses_with_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract responses that mention a specific program.
        
        Args:
            program_name: Name of the program
            responses_with_features: List of responses with extracted features
            
        Returns:
            List of responses mentioning the program
        """
        program_responses = []
        
        for resp_data in responses_with_features:
            response_text = resp_data.get('text', '')
            features = resp_data.get('features')
            
            # Check if program is mentioned
            if self.program_patterns[program_name].search(response_text):
                program_responses.append({
                    'response_id': resp_data['response_id'],
                    'text': response_text,
                    'features': features,
                    'question_id': resp_data.get('question_id')
                })
        
        return program_responses
    
    def analyze_program_themes(self, program_name: str, 
                             program_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze themes specific to a program using GPT-4.1.
        
        Args:
            program_name: Name of the program
            program_responses: Responses mentioning this program
            
        Returns:
            Dictionary of program-specific themes and insights
        """
        if not self.llm_client.client or not program_responses:
            return {}
        
        # Prepare response samples for analysis
        response_samples = []
        for i, resp in enumerate(program_responses[:50]):  # Limit to 50 for API
            response_samples.append(
                f"{i+1}. {resp['text'][:300]}..."
            )
        
        system_prompt = f"""You are a program evaluation specialist analyzing feedback for {program_name}.

## Identity
You extract actionable insights to improve cultural program effectiveness.

## Instructions
Analyze the feedback to identify:
1. Program strengths and successes
2. Areas needing improvement
3. Specific requests or suggestions
4. Impact statements from beneficiaries
5. Accessibility or barrier issues

Focus on concrete, actionable findings specific to {program_name}.

## ACCURACY
Extract only feedback explicitly about this program."""

        user_prompt = f"""Program: {program_name}
Total Mentions: {len(program_responses)}

Sample Feedback:
{chr(10).join(response_samples)}

Analyze this feedback and provide structured insights about the program."""

        try:
            # Add request for JSON output
            json_prompt = user_prompt + "\n\nReturn a JSON object with program analysis data."
            
            # Use LLMClient
            response = self.llm_client.generate_response(
                prompt=json_prompt,
                instructions=system_prompt,
                temperature=0.4
            )
            
            return json.loads(response.content)
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="analyze_program_themes",
                error_type=type(e).__name__,
                error_message=str(e),
                program=program_name
            )
            return {}
    
    def extract_quotes_and_evidence(self, program_name: str,
                                  program_responses: List[Dict[str, Any]]) -> List[str]:
        """
        Extract representative quotes about the program.
        
        Args:
            program_name: Name of the program
            program_responses: Responses mentioning this program
            
        Returns:
            List of representative quotes
        """
        quotes = []
        
        for resp in program_responses:
            text = resp['text']
            
            # Find sentences containing program name
            sentences = text.split('.')
            for sentence in sentences:
                if self.program_patterns[program_name].search(sentence):
                    quote = sentence.strip()
                    if 20 < len(quote) < 200:  # Reasonable quote length
                        quotes.append(quote)
        
        # Deduplicate and limit
        unique_quotes = list(set(quotes))[:10]
        
        return unique_quotes
    
    def analyze_program(self, program_name: str,
                       all_responses_with_features: List[Dict[str, Any]]) -> Optional[ProgramFeedback]:
        """
        Perform complete analysis for a single program.
        
        Args:
            program_name: Name of the program to analyze
            all_responses_with_features: All survey responses with extracted features
            
        Returns:
            ProgramFeedback object with analysis results
        """
        # Check cache
        cache_file = self.program_cache_dir / f"{program_name.replace(' ', '_').lower()}_analysis.json"
        if cache_file.exists():
            console.print(f"[dim]Loading cached analysis for {program_name}[/dim]")
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return ProgramFeedback(**data)
        
        console.print(f"\n[bold blue]Analyzing Program: {program_name}[/bold blue]")
        
        # Extract program-specific responses
        program_responses = self.extract_program_specific_feedback(
            program_name, all_responses_with_features
        )
        
        if not program_responses:
            console.print(f"[yellow]No mentions found for {program_name}[/yellow]")
            return None
        
        console.print(f"[green]Found {len(program_responses)} mentions of {program_name}[/green]")
        
        # Aggregate sentiment from features
        sentiment_summary = defaultdict(int)
        demographic_reach = defaultdict(int)
        
        for resp in program_responses:
            if resp.get('features'):
                features = ResponseFeatures(**resp['features'])
                sentiment_summary[features.sentiment] += 1
                
                # Track stakeholder types as proxy for demographics
                stakeholder = features.stakeholder_type.value
                demographic_reach[stakeholder] += 1
        
        # Analyze program themes
        theme_analysis = self.analyze_program_themes(program_name, program_responses)
        
        # Extract quotes
        quotes = self.extract_quotes_and_evidence(program_name, program_responses)
        
        # Create ProgramFeedback object
        feedback = ProgramFeedback(
            program_name=program_name,
            mention_count=len(program_responses),
            sentiment_summary=dict(sentiment_summary),
            strengths=theme_analysis.get('strengths', []),
            improvement_areas=theme_analysis.get('improvement_areas', []),
            specific_requests=theme_analysis.get('specific_requests', []),
            representative_quotes=quotes,
            impact_statements=theme_analysis.get('impact_statements', []),
            accessibility_issues=theme_analysis.get('accessibility_issues', []),
            demographic_reach=dict(demographic_reach)
        )
        
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(feedback.model_dump(), f, indent=2)
        
        self.audit_logger.log_operation(
            operation="program_analysis_complete",
            program_name=program_name,
            mention_count=feedback.mention_count,
            cache_file=str(cache_file)
        )
        
        # Display summary
        self._display_program_summary(feedback)
        
        return feedback
    
    def _display_program_summary(self, feedback: ProgramFeedback) -> None:
        """Display a summary of program analysis."""
        console.print(f"\n[bold green]Analysis Complete for {feedback.program_name}[/bold green]")
        
        # Create summary table
        table = Table(title=f"{feedback.program_name} Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Mentions", str(feedback.mention_count))
        table.add_row("Strengths Identified", str(len(feedback.strengths)))
        table.add_row("Improvement Areas", str(len(feedback.improvement_areas)))
        table.add_row("Specific Requests", str(len(feedback.specific_requests)))
        
        # Sentiment summary
        if feedback.sentiment_summary:
            sentiment_str = ", ".join([
                f"{k.value}: {v}" for k, v in feedback.sentiment_summary.items()
            ])
            table.add_row("Sentiment", sentiment_str)
        
        console.print(table)
        
        # Show sample feedback
        if feedback.strengths:
            console.print("\n[bold]Top Strengths:[/bold]")
            for i, strength in enumerate(feedback.strengths[:3], 1):
                console.print(f"{i}. {strength}")
        
        if feedback.improvement_areas:
            console.print("\n[bold]Key Improvement Areas:[/bold]")
            for i, area in enumerate(feedback.improvement_areas[:3], 1):
                console.print(f"{i}. {area}")
    
    def analyze_all_programs(self, all_responses: List[Dict[str, Any]]) -> Dict[str, ProgramFeedback]:
        """
        Analyze all cultural programs.
        
        Args:
            all_responses: All survey responses with text and metadata
            
        Returns:
            Dictionary mapping program names to ProgramFeedback objects
        """
        console.print(f"\n[bold]Analyzing {len(self.CULTURAL_PROGRAMS)} Cultural Programs...[/bold]")
        
        # First, extract features for all responses if not already done
        responses_with_features = []
        
        with console.status("[bold green]Extracting features from responses...") as status:
            for resp in track(all_responses, description="Processing responses"):
                # Check if response has text
                if resp.get('text', '').strip():
                    # Check if any program is mentioned
                    mentioned_programs = []
                    for program in self.CULTURAL_PROGRAMS:
                        if self.program_patterns[program].search(resp['text']):
                            mentioned_programs.append(program)
                    
                    if mentioned_programs:
                        # Extract features for this response
                        features = self.feature_extractor.extract_features(
                            response=resp['text'],
                            question=resp.get('question_text', ''),
                            response_id=resp['id'],
                            question_id=resp.get('question_id', '')
                        )
                        
                        if features:
                            responses_with_features.append({
                                'response_id': resp['id'],
                                'text': resp['text'],
                                'features': features.model_dump(),
                                'question_id': resp.get('question_id'),
                                'mentioned_programs': mentioned_programs
                            })
        
        console.print(f"[green]✓[/green] Found {len(responses_with_features)} responses mentioning programs")
        
        # Analyze each program
        program_analyses = {}
        
        for program in self.CULTURAL_PROGRAMS:
            analysis = self.analyze_program(program, responses_with_features)
            if analysis:
                program_analyses[program] = analysis
        
        # Summary report
        console.print(f"\n[bold green]✓ Completed analysis for {len(program_analyses)} programs[/bold green]")
        
        # Save summary
        summary_file = self.program_cache_dir / "program_analysis_summary.json"
        summary_data = {
            'analysis_date': datetime.now().isoformat(),
            'programs_analyzed': len(program_analyses),
            'total_program_mentions': sum(p.mention_count for p in program_analyses.values()),
            'program_summaries': {
                name: {
                    'mentions': feedback.mention_count,
                    'strengths_count': len(feedback.strengths),
                    'improvements_count': len(feedback.improvement_areas)
                }
                for name, feedback in program_analyses.items()
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        return program_analyses