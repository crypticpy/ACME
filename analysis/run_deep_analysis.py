#!/usr/bin/env python3
"""
Run deep qualitative analysis using GPT-4.1 structured outputs.

This script implements the analysis pipeline described in PROJECT_PLAN.md,
processing all 10,588 responses through multiple analysis passes.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.config import settings
from src.validation.audit import AuditLogger
from src.ingestion.loader import DataLoader
from src.features import (
    QuestionAnalyzer,
    CrossQuestionSynthesizer,
    ProgramAnalyzer
)

console = Console()


def load_survey_data(audit_logger: AuditLogger) -> Dict[str, Any]:
    """Load and prepare survey data for analysis."""
    console.print("\n[bold blue]Loading Survey Data...[/bold blue]")
    
    loader = DataLoader(audit_logger)
    
    # Load all data
    data = loader.load_all_data()
    survey_df = data.get("survey")
    
    if survey_df is None or survey_df.empty:
        raise ValueError("No survey data found!")
    
    console.print(f"[green]✓[/green] Loaded {len(survey_df)} survey responses")
    
    # Extract text responses from survey data
    all_responses = []
    response_id = 1
    
    # Define question mappings based on actual survey columns
    questions = [
        {"id": "q1_org_support", "text": "How do you believe ACME should better support organizations and cultural leaders?", 
         "column": "austins_creative_community_has_built_a_strong_foundation_of_existing_organizations_that_informs_acmes_goals_and_mission_how_do_you_believe_acme_should_better_support_these_organizations_and_cul"},
        {"id": "q2_opportunities", "text": "What type of cultural arts or entertainment opportunities would you like to see more of in Austin?",
         "column": "what_type_of_cultural_arts_or_entertainment_opportunities_would_you_like_to_see_more_of_in_austin"},
        {"id": "q3_improvements", "text": "What improvements would you like to see in these cultural funding programs?",
         "column": "what_improvements_would_you_like_to_see_in_these_cultural_funding_programs"},
        {"id": "q4_barriers", "text": "What barriers do you or your community face in accessing support or services related to arts, culture, music and entertainment?",
         "column": "what_barriers_do_you_or_your_community_face_in_accessing_support_or_services_related_to_arts_culture_music_and_entertainment"},
        {"id": "q5_new_programs", "text": "What kinds of programs or services would you like ACME to offer that currently do not exist or are underrepresented?",
         "column": "what_kinds_of_programs_or_services_would_you_like_acme_to_offer_that_currently_do_not_exist_or_are_underrepresented"},
        {"id": "q6_feedback", "text": "Do you have any additional ideas, concerns, or feedback you would like to share to help ACME better serve the public?",
         "column": "do_you_have_any_additional_ideas_concerns_or_feedback_you_would_like_to_share_to_help_acme_better_serve_the_public"}
    ]
    
    # Identify specific text columns to analyze
    text_columns = [q["column"] for q in questions if "column" in q]
    
    console.print(f"[dim]Found {len(text_columns)} text response columns[/dim]")
    
    # Extract all text responses
    for idx, row in survey_df.iterrows():
        for question in questions:
            col = question['column']
            text = row.get(col, '')
            if isinstance(text, str) and text.strip() and len(text.strip()) > 10:
                all_responses.append({
                    'id': f'resp_{response_id}',
                    'text': text.strip(),
                    'question_id': question['id'],
                    'question_text': question['text'],
                    'source': 'survey',
                    'respondent_idx': idx
                })
                response_id += 1
    
    console.print(f"\n[bold green]Total text responses found: {len(all_responses)}[/bold green]")
    
    return {
        'responses': all_responses,
        'questions': questions,
        'survey_data': survey_df,
        'all_data': data
    }


def run_deep_analysis():
    """Execute the complete deep analysis pipeline."""
    start_time = datetime.now()
    
    console.print(Panel.fit(
        "[bold]ACME Cultural Funding Deep Analysis[/bold]\n"
        "Using GPT-4.1 with Structured Outputs",
        style="bold blue"
    ))
    
    # Initialize audit logger
    audit_logger = AuditLogger()
    audit_logger.log_operation(
        operation="deep_analysis_start",
        timestamp=start_time.isoformat()
    )
    
    try:
        # Load survey data
        data = load_survey_data(audit_logger)
        responses = data['responses']
        questions = data['questions']
        
        if not responses:
            console.print("[red]No text responses found to analyze![/red]")
            return
        
        # Phase 1: Question-level analysis
        console.print("\n[bold yellow]Phase 1: Question-Level Analysis[/bold yellow]")
        question_analyzer = QuestionAnalyzer(audit_logger)
        
        question_analyses = []
        for question in questions:
            # Filter responses for this question
            question_responses = [r for r in responses if r['question_id'] == question['id']]
            
            if question_responses:
                console.print(f"\n[dim]Found {len(question_responses)} responses for {question['id']}[/dim]")
                analysis = question_analyzer.analyze_question(
                    question_id=question['id'],
                    question_text=question['text'],
                    all_responses=responses
                )
                
                if analysis:
                    question_analyses.append(analysis)
        
        console.print(f"\n[bold green]✓ Completed {len(question_analyses)} question analyses[/bold green]")
        
        # Phase 2: Cross-question synthesis
        console.print("\n[bold yellow]Phase 2: Cross-Question Synthesis[/bold yellow]")
        synthesizer = CrossQuestionSynthesizer(audit_logger)
        
        synthesis_results = synthesizer.synthesize_insights(question_analyses)
        
        # Phase 3: Program-specific analysis
        console.print("\n[bold yellow]Phase 3: Program-Specific Analysis[/bold yellow]")
        program_analyzer = ProgramAnalyzer(audit_logger)
        
        program_results = program_analyzer.analyze_all_programs(responses)
        
        # Save comprehensive results
        results_dir = settings.data_dir / "results" / "deep_analysis"
        results_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"deep_analysis_results_{timestamp}.json"
        
        comprehensive_results = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_responses': len(responses),
                'questions_analyzed': len(question_analyses),
                'programs_analyzed': len(program_results),
                'gpt_model': 'gpt-4.1',
                'analysis_duration': str(datetime.now() - start_time)
            },
            'question_analyses': [qa.model_dump() for qa in question_analyses],
            'cross_question_synthesis': synthesis_results,
            'program_analyses': {
                name: feedback.model_dump() 
                for name, feedback in program_results.items()
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(comprehensive_results, f, indent=2)
        
        console.print(f"\n[bold green]✓ Analysis complete! Results saved to:[/bold green]")
        console.print(f"  {results_file}")
        
        # Display executive summary
        display_executive_summary(comprehensive_results)
        
        # Log completion
        audit_logger.log_operation(
            operation="deep_analysis_complete",
            duration=str(datetime.now() - start_time),
            results_file=str(results_file),
            total_responses=len(responses)
        )
        
    except Exception as e:
        console.print(f"\n[red]Error during analysis: {str(e)}[/red]")
        audit_logger.log_error(
            operation="deep_analysis_error",
            error_type=type(e).__name__,
            error_message=str(e),
            context={}
        )
        raise


def display_executive_summary(results: Dict[str, Any]):
    """Display executive summary of analysis results."""
    console.print("\n" + "="*60)
    console.print("[bold]EXECUTIVE SUMMARY[/bold]")
    console.print("="*60)
    
    metadata = results['metadata']
    synthesis = results['cross_question_synthesis']
    
    # Key metrics
    console.print(f"\n[bold]Analysis Metrics:[/bold]")
    console.print(f"• Total Responses Analyzed: {metadata['total_responses']:,}")
    console.print(f"• Questions Analyzed: {metadata['questions_analyzed']}")
    console.print(f"• Programs Analyzed: {metadata['programs_analyzed']}")
    console.print(f"• Analysis Duration: {metadata['analysis_duration']}")
    
    # Top recurring themes
    if synthesis and 'recurring_themes' in synthesis:
        console.print(f"\n[bold]Top 5 Recurring Themes:[/bold]")
        themes = list(synthesis['recurring_themes'].items())[:5]
        for i, (theme, data) in enumerate(themes, 1):
            console.print(
                f"{i}. {theme.title()} - {data['total_mentions']} mentions "
                f"across {data['question_count']} questions"
            )
    
    # Strategic insights
    if synthesis and 'strategic_insights' in synthesis:
        console.print(f"\n[bold]Key Strategic Insights:[/bold]")
        for i, insight in enumerate(synthesis['strategic_insights'][:3], 1):
            console.print(f"{i}. {insight}")
    
    # Program highlights
    if results['program_analyses']:
        console.print(f"\n[bold]Program Analysis Highlights:[/bold]")
        
        # Sort programs by mention count
        programs = sorted(
            results['program_analyses'].items(),
            key=lambda x: x[1]['mention_count'],
            reverse=True
        )
        
        for program, data in programs[:3]:
            console.print(f"\n• {program}: {data['mention_count']} mentions")
            if data['strengths']:
                console.print(f"  Top strength: {data['strengths'][0]}")
            if data['improvement_areas']:
                console.print(f"  Key improvement: {data['improvement_areas'][0]}")
    
    console.print("\n" + "="*60)


def main():
    """Main entry point."""
    try:
        # Check for API key (Azure or standard OpenAI)
        if not (settings.azure_openai_api_key and settings.azure_openai_endpoint) and not settings.openai_api_key:
            console.print("[red]Error: No LLM API credentials found![/red]")
            console.print("Please set either:")
            console.print("  - Azure OpenAI: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
            console.print("  - Standard OpenAI: OPENAI_API_KEY")
            console.print("in your analysis/.env file")
            sys.exit(1)
        
        # Run analysis
        run_deep_analysis()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()