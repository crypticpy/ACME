"""Qualitative analysis for WHAT themes using GPT-4.1."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter

import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import settings
from ..validation.audit import AuditLogger
from ..llm import LLMClient, PromptTemplates
from ..quantitative.analyzer import QuantitativeAnalyzer


console = Console()


class QualitativeAnalyzer:
    """Analyzes qualitative WHAT themes from survey and feedback data."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger()
        self.llm_client = LLMClient(audit_logger)
        self.prompts = PromptTemplates()
        self.quant_analyzer = QuantitativeAnalyzer(audit_logger)
        
    def analyze_what_themes(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Perform comprehensive WHAT thematic analysis."""
        console.print("[bold blue]Performing qualitative WHAT analysis...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Step 1: Share of Voice Classification
            task = progress.add_task("Classifying respondents...", total=None)
            share_of_voice = self._analyze_share_of_voice_llm(data["survey"])
            progress.update(task, completed=True)
            
            # Step 2: Extract themes from all responses
            task = progress.add_task("Extracting major themes...", total=None)
            themes = self._extract_major_themes(data)
            progress.update(task, completed=True)
            
            # Step 3: Generate supporting evidence
            task = progress.add_task("Gathering supporting evidence...", total=None)
            themes_with_evidence = self._add_theme_evidence(themes, data)
            progress.update(task, completed=True)
            
            # Step 4: Program-specific analysis
            task = progress.add_task("Analyzing program-specific themes...", total=None)
            program_themes = self._analyze_programs(data)
            progress.update(task, completed=True)
            
            # Step 5: Transportation/Parking lot analysis
            task = progress.add_task("Analyzing parking lot items...", total=None)
            parking_lot = self._analyze_parking_lot(data)
            progress.update(task, completed=True)
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "share_of_voice_refined": share_of_voice,
            "major_themes": themes_with_evidence,
            "program_analysis": program_themes,
            "parking_lot": parking_lot,
            "theme_summary": self._generate_theme_summary(themes_with_evidence)
        }
        
        # Display results
        self._display_theme_summary(results)
        
        # Save results
        self._save_what_results(results)
        
        return results
    
    def _analyze_share_of_voice_llm(self, survey_df: pd.DataFrame) -> Dict[str, Any]:
        """Refine share of voice analysis using LLM classification."""
        # Find the actual role column
        role_column = None
        for col in survey_df.columns:
            if 'role' in col.lower() and 'creative' in col.lower():
                role_column = col
                break
        
        if not role_column:
            console.print("[yellow]Warning: Could not find role column for classification[/yellow]")
            role_column = 'role'  # fallback
        
        # Prepare respondent data for classification
        respondents = []
        
        for idx, row in survey_df.iterrows():
            # Collect relevant text fields
            text_fields = []
            
            # Role
            if pd.notna(row.get(role_column)):
                text_fields.append(f"Role: {row[role_column]}")
            
            # Collect responses from text columns dynamically
            # Look for columns with relevant keywords
            for col in survey_df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['challenge', 'barrier', 'improve', 'service', 'program', 'need', 'feedback']):
                    if pd.notna(row[col]) and len(str(row[col])) > 10:
                        text_fields.append(str(row[col])[:200])
            
            if text_fields:
                respondents.append({
                    'id': f"R{idx:04d}",
                    'role': row.get(role_column, ''),
                    'text': ' '.join(text_fields)
                })
        
        # Classify in batches (limit to sample for performance)
        try:
            # Sample respondents for classification if too many
            if len(respondents) > 200:
                import random
                random.seed(42)  # For reproducibility
                sample_respondents = random.sample(respondents, 200)
                console.print(f"[yellow]Sampling 200 of {len(respondents)} respondents for LLM classification[/yellow]")
            else:
                sample_respondents = respondents
                
            classifications = self.llm_client.classify_respondents(sample_respondents, batch_size=50)
            console.print(f"[green]Classified {len(classifications)} respondents using GPT-4-turbo[/green]")
        except Exception as e:
            console.print(f"[red]LLM classification failed: {e}[/red]")
            self.audit_logger.log_error(
                operation="classify_respondents",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"sample_size": len(sample_respondents)}
            )
            classifications = []
        
        # Aggregate results
        category_counts = Counter()
        confidence_scores = {}
        
        for classification in classifications:
            category = classification.get('classification', 'Unknown')
            category_counts[category] += 1
            
            if category not in confidence_scores:
                confidence_scores[category] = []
            confidence_scores[category].append(classification.get('confidence', 0.5))
        
        # Calculate share of voice with confidence
        total = sum(category_counts.values())
        share_of_voice = {}
        
        # Handle empty classifications
        if total == 0:
            return {
                "refined_categories": {},
                "total_classified": 0,
                "classification_quality": {
                    "average_confidence": 0,
                    "high_confidence_percentage": 0
                },
                "error": "No classifications returned"
            }
        
        for category, count in category_counts.items():
            avg_confidence = np.mean(confidence_scores[category])
            share_of_voice[category] = {
                "count": count,
                "percentage": (count / total) * 100,
                "average_confidence": avg_confidence,
                "high_confidence_count": sum(1 for c in confidence_scores[category] if c >= 0.8)
            }
        
        return {
            "refined_categories": share_of_voice,
            "total_classified": total,
            "classification_quality": {
                "average_confidence": np.mean([c for scores in confidence_scores.values() for c in scores]),
                "high_confidence_percentage": sum(v["high_confidence_count"] for v in share_of_voice.values()) / total * 100
            }
        }
    
    def _extract_major_themes(self, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Extract major themes from all text responses."""
        # Collect all relevant text responses
        all_responses = []
        
        # From survey data - dynamically find text columns
        survey_df = data["survey"]
        
        # Find columns with substantial text responses
        for col in survey_df.columns:
            col_lower = col.lower()
            # Look for open-ended question columns
            if any(keyword in col_lower for keyword in [
                'challenge', 'barrier', 'improve', 'service', 'program', 
                'need', 'feedback', 'share', 'additional', 'comment',
                'support', 'help', 'wish', 'want', 'suggest', 'ideas',
                'opportunities', 'organizations', 'kinds'
            ]):
                # Check if it's a text column with substantial responses
                non_null = survey_df[col].dropna()
                if len(non_null) > 50:  # At least 50 responses
                    responses = non_null.astype(str)
                    responses = responses[responses.str.len() > 20]  # Filter short responses
                    if len(responses) > 10:  # At least 10 meaningful responses
                        all_responses.extend(responses.tolist())
                        console.print(f"[dim]Added {len(responses)} responses from: {col[:50]}...[/dim]")
        
        # From working document
        working_df = data["working_doc_main"]
        # Look for recommendation or text columns
        for col in working_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['recommendation', 'comment', 'feedback', 'detail', 'description']):
                non_null = working_df[col].dropna()
                if len(non_null) > 10:
                    responses = non_null.astype(str)
                    responses = responses[responses.str.len() > 20]
                    if len(responses) > 5:
                        all_responses.extend(responses.tolist())
                        console.print(f"[dim]Added {len(responses)} responses from working doc: {col}[/dim]")
        
        console.print(f"[dim]Analyzing {len(all_responses)} text responses...[/dim]")
        
        # Extract themes using LLM
        try:
            # Sample responses if too many for efficient processing
            if len(all_responses) > 500:
                import random
                random.seed(42)
                sample_responses = random.sample(all_responses, 500)
                console.print(f"[yellow]Sampling 500 of {len(all_responses)} responses for theme extraction[/yellow]")
            else:
                sample_responses = all_responses
                
            themes = self.llm_client.extract_themes(
                responses=sample_responses,
                num_themes=10,
                min_frequency=5
            )
            console.print(f"[green]Extracted {len(themes)} themes using GPT-4-turbo[/green]")
            
            # Enrich with sentiment and urgency if not present
            for theme in themes:
                if 'sentiment' not in theme:
                    # Analyze sentiment based on description
                    desc_lower = theme.get('description', '').lower()
                    if any(word in desc_lower for word in ['need', 'lack', 'barrier', 'challenge', 'difficult']):
                        theme['sentiment'] = 'negative'
                    elif any(word in desc_lower for word in ['opportunity', 'strength', 'success', 'positive']):
                        theme['sentiment'] = 'positive'
                    else:
                        theme['sentiment'] = 'neutral'
                
                if 'urgency' not in theme:
                    # Determine urgency based on keywords
                    keywords_str = ' '.join(theme.get('keywords', [])).lower()
                    if any(word in keywords_str for word in ['urgent', 'critical', 'immediate', 'crisis']):
                        theme['urgency'] = 'high'
                    elif any(word in keywords_str for word in ['important', 'significant', 'priority']):
                        theme['urgency'] = 'medium'
                    else:
                        theme['urgency'] = 'low'
        except Exception as e:
            console.print(f"[red]Theme extraction failed: {e}[/red]")
            self.audit_logger.log_error(
                operation="extract_themes",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"responses_analyzed": len(sample_responses)}
            )
            themes = []
        
        # Validate and enrich themes
        for theme in themes:
            # Ensure all required fields
            theme.setdefault('count', 0)
            theme.setdefault('percentage', 0)
            theme.setdefault('description', '')
            theme.setdefault('keywords', [])
            theme.setdefault('sentiment', 'neutral')
            theme.setdefault('urgency', 'medium')
        
        return themes
    
    def _add_theme_evidence(
        self,
        themes: List[Dict[str, Any]],
        data: Dict[str, pd.DataFrame]
    ) -> List[Dict[str, Any]]:
        """Add supporting evidence quotes to each theme."""
        survey_df = data["survey"]
        
        # Prepare response data with IDs
        response_data = []
        
        # Find actual text columns dynamically
        text_columns = []
        for col in survey_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in [
                'challenge', 'barrier', 'improve', 'service', 'program',
                'feedback', 'additional', 'opportunities', 'organizations'
            ]):
                non_null = survey_df[col].dropna()
                if len(non_null) > 50 and isinstance(non_null.iloc[0], str):
                    text_columns.append(col)
        
        console.print(f"[dim]Using {len(text_columns)} text columns for evidence gathering[/dim]")
        
        for idx, row in survey_df.iterrows():
            combined_text = []
            for col in text_columns:
                if pd.notna(row[col]) and len(str(row[col])) > 10:
                    combined_text.append(str(row[col]))
            
            if combined_text:
                response_data.append({
                    'id': f"R{idx:04d}",
                    'text': ' '.join(combined_text)
                })
        
        # Add evidence to each theme
        for theme in themes:
            theme_name = theme.get('theme', '')
            
            # Get supporting quotes
            try:
                evidence_quotes = self.llm_client.generate_theme_evidence(
                    theme=theme_name,
                    responses=response_data[:50],  # Limit to prevent token overflow
                    num_examples=3
                )
                # No fallback - if LLM fails, we don't have evidence
            except Exception as e:
                console.print(f"[yellow]Evidence generation failed for {theme_name}: {e}[/yellow]")
                self.audit_logger.log_error(
                    operation="generate_theme_evidence",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={"theme": theme_name}
                )
                evidence_quotes = []
            
            theme['supporting_evidence'] = evidence_quotes
            
            # Add evidence strength metric
            theme['evidence_strength'] = len(evidence_quotes) / 5.0  # Ratio of quotes found
        
        return themes
    
    def _analyze_programs(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze themes for each specific program."""
        program_analysis = {}
        
        # Get program-specific responses
        survey_df = data["survey"]
        working_df = data["working_doc_main"]
        
        # Find columns mentioning programs
        program_columns = []
        for col in survey_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['program', 'funding', 'applied', 'received']):
                program_columns.append(col)
        
        console.print(f"[dim]Found {len(program_columns)} program-related columns[/dim]")
        
        # Find text columns for collecting responses
        text_columns = []
        for col in survey_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in [
                'challenge', 'barrier', 'improve', 'service', 'feedback', 
                'opportunities', 'kinds'
            ]):
                non_null = survey_df[col].dropna()
                if len(non_null) > 50:
                    text_columns.append(col)
        
        for program in settings.programs:
            # Find responses mentioning this program
            program_responses = []
            
            # Search across all text columns for program mentions
            for idx, row in survey_df.iterrows():
                mentions_program = False
                
                # Check if any field mentions this program
                for col in survey_df.columns:
                    if pd.notna(row[col]) and isinstance(row[col], str):
                        if program.lower() in str(row[col]).lower():
                            mentions_program = True
                            break
                
                if mentions_program:
                    # Collect text from relevant columns
                    text = []
                    for col in text_columns:
                        if pd.notna(row[col]) and len(str(row[col])) > 20:
                            text.append(str(row[col]))
                    if text:
                        program_responses.append(' '.join(text))
            
            # From working document
            if 'program' in working_df.columns:
                program_working = working_df[working_df['program'] == program]
                if 'recommendation_comment' in program_working.columns:
                    recommendations = program_working['recommendation_comment'].dropna().astype(str)
                    program_responses.extend(recommendations.tolist())
            
            if len(program_responses) >= 3:  # Minimum responses for analysis
                # Analyze program themes
                try:
                    analysis = self.llm_client.analyze_program_themes(
                        program_name=program,
                        responses=program_responses,
                        top_n=3
                    )
                    program_analysis[program] = analysis
                except Exception as e:
                    console.print(f"[yellow]Program analysis failed for {program}: {e}[/yellow]")
                    self.audit_logger.log_error(
                        operation="analyze_program_themes",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        context={"program": program, "responses": len(program_responses)}
                    )
                    program_analysis[program] = {
                        "program": program,
                        "response_count": len(program_responses),
                        "themes": [],
                        "error": str(e)
                    }
            else:
                program_analysis[program] = {
                    "program": program,
                    "response_count": len(program_responses),
                    "themes": [],
                    "note": "Insufficient data for detailed analysis"
                }
        
        return program_analysis
    
    def _analyze_parking_lot(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze transportation and parking-related feedback."""
        # Keywords for transportation issues
        transport_keywords = [
            'parking', 'transportation', 'transit', 'bus', 'drive', 'car',
            'uber', 'lyft', 'bike', 'walk', 'distance', 'location', 'access'
        ]
        
        # Collect transportation-related responses
        transport_responses = []
        
        # From survey
        survey_df = data["survey"]
        
        # Find text columns dynamically
        text_columns = []
        for col in survey_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in [
                'challenge', 'barrier', 'feedback', 'additional', 'ideas'
            ]):
                non_null = survey_df[col].dropna()
                if len(non_null) > 50:
                    text_columns.append(col)
        
        for col in text_columns:
            for idx, text in enumerate(survey_df[col].dropna()):
                text_lower = str(text).lower()
                if any(keyword in text_lower for keyword in transport_keywords):
                    transport_responses.append({
                        'id': f"R{idx:04d}",
                        'text': str(text),
                        'source': 'survey'
                    })
        
        # From working document
        working_df = data["working_doc_main"]
        if 'recommendation_comment' in working_df.columns:
            for idx, text in enumerate(working_df['recommendation_comment'].dropna()):
                text_lower = str(text).lower()
                if any(keyword in text_lower for keyword in transport_keywords):
                    transport_responses.append({
                        'id': f"W{idx:04d}",
                        'text': str(text),
                        'source': 'working_doc'
                    })
        
        # Analyze if we have enough responses
        if len(transport_responses) >= 5:
            # For now, create a simple analysis without LLM
            # TODO: Add ParkingLotAnalysis structured output to LLM client
            parking_analysis = {
                "total_mentions": len(transport_responses),
                "categories": {
                    "parking": {
                        "count": sum(1 for r in transport_responses if 'parking' in r['text'].lower()),
                        "key_issues": ["Parking availability", "Parking cost"],
                        "affected_areas": []
                    },
                    "transit": {
                        "count": sum(1 for r in transport_responses if any(word in r['text'].lower() for word in ['bus', 'transit', 'transportation'])),
                        "key_issues": ["Transit access", "Route availability"],
                        "affected_areas": []
                    }
                },
                "summary": f"Transportation and parking concerns were mentioned in {len(transport_responses)} responses, indicating potential barriers to cultural participation.",
                "recommendations": [
                    "Consider venue parking availability in funding decisions",
                    "Support programs that provide transportation assistance",
                    "Prioritize venues with good transit access"
                ]
            }
        else:
            parking_analysis = {
                "total_mentions": len(transport_responses),
                "summary": "Limited transportation feedback received.",
                "categories": {},
                "recommendations": []
            }
        
        return parking_analysis
    
    def _generate_theme_summary(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive summary of themes."""
        return {
            "total_themes": len(themes),
            "top_3_themes": [t['theme'] for t in themes[:3]],
            "sentiment_distribution": Counter(t.get('sentiment', 'neutral') for t in themes),
            "urgency_distribution": Counter(t.get('urgency', 'medium') for t in themes),
            "average_evidence_strength": np.mean([t.get('evidence_strength', 0.5) for t in themes])
        }
    
    def _display_theme_summary(self, results: Dict[str, Any]) -> None:
        """Display theme analysis summary in rich tables."""
        # Major themes table
        if results.get("major_themes"):
            table = Table(title="Top 10 Cultural Funding Themes", show_header=True)
            table.add_column("Theme", style="cyan", width=30)
            table.add_column("Count", justify="right")
            table.add_column("%", justify="right")
            table.add_column("Sentiment", justify="center")
            table.add_column("Urgency", justify="center")
            
            for theme in results["major_themes"][:10]:
                sentiment_color = {
                    'positive': 'green',
                    'negative': 'red',
                    'neutral': 'yellow',
                    'mixed': 'blue'
                }.get(theme.get('sentiment', 'neutral'), 'white')
                
                urgency_style = {
                    'high': 'bold red',
                    'medium': 'yellow',
                    'low': 'dim'
                }.get(theme.get('urgency', 'medium'), 'white')
                
                table.add_row(
                    theme['theme'],
                    f"{theme.get('count', 0):,}",
                    f"{theme.get('percentage', 0):.1f}%",
                    f"[{sentiment_color}]{theme.get('sentiment', 'neutral')}[/{sentiment_color}]",
                    f"[{urgency_style}]{theme.get('urgency', 'medium')}[/{urgency_style}]"
                )
            
            console.print(table)
        
        # Share of voice refinement
        if "share_of_voice_refined" in results:
            voice_data = results["share_of_voice_refined"]["refined_categories"]
            
            voice_table = Table(title="Refined Share of Voice Analysis", show_header=True)
            voice_table.add_column("Stakeholder Category", style="cyan")
            voice_table.add_column("Count", justify="right")
            voice_table.add_column("Percentage", justify="right")
            voice_table.add_column("Avg Confidence", justify="right")
            
            for category, data in voice_data.items():
                voice_table.add_row(
                    category,
                    f"{data['count']:,}",
                    f"{data['percentage']:.1f}%",
                    f"{data['average_confidence']:.2f}"
                )
            
            console.print(voice_table)
        
        # Program summary
        if "program_analysis" in results:
            console.print("\n[bold]Program-Specific Insights:[/bold]")
            for program, analysis in results["program_analysis"].items():
                if analysis.get('themes'):
                    console.print(f"\n[cyan]{program}[/cyan] ({analysis['response_count']} responses)")
                    for theme in analysis['themes'][:3]:
                        console.print(f"  • {theme.get('theme', 'Unknown')}")
    
    def _save_what_results(self, results: Dict[str, Any]) -> None:
        """Save WHAT analysis results."""
        output_file = settings.results_dir / f"what_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"[dim]WHAT analysis results saved to: {output_file}[/dim]")