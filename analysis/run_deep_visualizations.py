#!/usr/bin/env python3
"""
Generate comprehensive visualizations for deep analysis results.

This script creates all visualization outputs from the deep qualitative analysis,
including question dashboards, theme evolution charts, and executive summaries.
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
from src.visualization.deep_analysis_charts import DeepAnalysisVisualizer

console = Console()


def load_deep_analysis_results() -> Dict[str, Any]:
    """Load the most recent deep analysis results."""
    results_dir = settings.data_dir / "results" / "deep_analysis"
    
    if not results_dir.exists():
        console.print("[red]No deep analysis results found![/red]")
        console.print("Please run 'poetry run python run_deep_analysis.py' first.")
        return None
    
    # Find most recent results file
    result_files = list(results_dir.glob("deep_analysis_results_*.json"))
    
    if not result_files:
        console.print("[red]No analysis result files found![/red]")
        return None
    
    latest_file = sorted(result_files)[-1]
    console.print(f"[dim]Loading results from: {latest_file.name}[/dim]")
    
    with open(latest_file, 'r') as f:
        return json.load(f)


def generate_visualizations(results: Dict[str, Any]):
    """Generate all visualizations from deep analysis results."""
    start_time = datetime.now()
    
    # Create output directory
    viz_dir = settings.results_dir / "visualizations" / "deep_analysis"
    viz_dir.mkdir(exist_ok=True, parents=True)
    
    # Add timestamp to output subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = viz_dir / f"viz_{timestamp}"
    output_dir.mkdir(exist_ok=True)
    
    visualizer = DeepAnalysisVisualizer()
    generated_files = []
    
    try:
        # 1. Question-specific dashboards
        console.print("\n[bold yellow]Creating Question Dashboards...[/bold yellow]")
        question_analyses = results.get('question_analyses', [])
        
        question_dir = output_dir / "questions"
        question_dir.mkdir(exist_ok=True)
        
        for q_analysis in question_analyses[:5]:  # Limit to first 5 for demo
            q_id = q_analysis.get('question_id', 'unknown')
            dashboard_path = question_dir / f"dashboard_{q_id}.html"
            
            visualizer.create_question_dashboard(q_analysis, dashboard_path)
            generated_files.append(str(dashboard_path))
        
        # 2. Theme evolution chart
        console.print("\n[bold yellow]Creating Theme Evolution Chart...[/bold yellow]")
        if len(question_analyses) > 1:
            evolution_path = output_dir / "theme_evolution.html"
            visualizer.create_theme_evolution_chart(question_analyses, evolution_path)
            generated_files.append(str(evolution_path))
        
        # 3. Stakeholder comparison matrix
        console.print("\n[bold yellow]Creating Stakeholder Comparison Matrix...[/bold yellow]")
        if len(question_analyses) > 1:
            matrix_path = output_dir / "stakeholder_matrix.html"
            visualizer.create_stakeholder_comparison_matrix(question_analyses, matrix_path)
            generated_files.append(str(matrix_path))
        
        # 4. Sentiment-urgency scatter plot
        console.print("\n[bold yellow]Creating Sentiment-Urgency Analysis...[/bold yellow]")
        all_themes = []
        for q_analysis in question_analyses:
            all_themes.extend(q_analysis.get('dominant_themes', []))
        
        if all_themes:
            scatter_path = output_dir / "sentiment_urgency_scatter.html"
            visualizer.create_sentiment_urgency_scatter(all_themes, scatter_path)
            generated_files.append(str(scatter_path))
        
        # 5. Program feedback sunburst
        console.print("\n[bold yellow]Creating Program Feedback Visualization...[/bold yellow]")
        program_analyses = results.get('program_analyses', {})
        
        if program_analyses:
            sunburst_path = output_dir / "program_feedback_sunburst.html"
            visualizer.create_program_feedback_sunburst(program_analyses, sunburst_path)
            generated_files.append(str(sunburst_path))
        
        # 6. Cross-question insights network
        console.print("\n[bold yellow]Creating Insights Network Graph...[/bold yellow]")
        synthesis = results.get('cross_question_synthesis', {})
        systemic_issues = synthesis.get('systemic_issues', [])
        
        if systemic_issues:
            network_path = output_dir / "insights_network.html"
            visualizer.create_insight_network_graph(systemic_issues, network_path)
            generated_files.append(str(network_path))
        
        # 7. Executive summary infographic
        console.print("\n[bold yellow]Creating Executive Summary...[/bold yellow]")
        if synthesis:
            summary_path = output_dir / "executive_summary.png"
            visualizer.create_executive_summary_infographic(synthesis, summary_path)
            generated_files.append(str(summary_path))
        
        # Create index file
        create_visualization_index(output_dir, generated_files)
        
        # Summary
        duration = datetime.now() - start_time
        console.print(f"\n[bold green]✓ Visualization generation complete![/bold green]")
        console.print(f"Generated {len(generated_files)} visualization files")
        console.print(f"Duration: {duration}")
        console.print(f"\nOutput directory: {output_dir}")
        
        # Show key insights
        display_key_insights(results)
        
    except Exception as e:
        console.print(f"\n[red]Error generating visualizations: {str(e)}[/red]")
        raise


def create_visualization_index(output_dir: Path, files: List[str]):
    """Create an HTML index file for all visualizations."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>ACME Deep Analysis Visualizations</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .viz-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .viz-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .viz-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .viz-card h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .viz-card a {
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        .viz-card a:hover {
            background-color: #2980b9;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>ACME Cultural Funding - Deep Analysis Visualizations</h1>
    <p class="timestamp">Generated: {timestamp}</p>
    
    <h2>Interactive Visualizations</h2>
    <div class="viz-grid">
"""
    
    # Add cards for each visualization
    for file_path in files:
        file_path = Path(file_path)
        if file_path.suffix == '.html':
            relative_path = file_path.relative_to(output_dir)
            
            # Determine visualization type
            if 'dashboard' in file_path.name:
                title = f"Question Dashboard: {file_path.stem.split('_')[-1]}"
                description = "Comprehensive analysis dashboard for individual question"
            elif 'evolution' in file_path.name:
                title = "Theme Evolution Chart"
                description = "Shows how themes evolve across different questions"
            elif 'matrix' in file_path.name:
                title = "Stakeholder Comparison Matrix"
                description = "Compares stakeholder participation across questions"
            elif 'scatter' in file_path.name:
                title = "Sentiment-Urgency Analysis"
                description = "Plots themes by sentiment and urgency scores"
            elif 'sunburst' in file_path.name:
                title = "Program Feedback Distribution"
                description = "Hierarchical view of program feedback by sentiment"
            elif 'network' in file_path.name:
                title = "Insights Network Graph"
                description = "Shows connections between insights and questions"
            else:
                title = file_path.stem.replace('_', ' ').title()
                description = "Data visualization"
            
            html_content += f"""
        <div class="viz-card">
            <h3>{title}</h3>
            <p>{description}</p>
            <a href="{relative_path}" target="_blank">View Visualization</a>
        </div>
"""
    
    # Add static images
    html_content += """
    </div>
    
    <h2>Static Reports</h2>
    <div class="viz-grid">
"""
    
    for file_path in files:
        file_path = Path(file_path)
        if file_path.suffix in ['.png', '.jpg']:
            relative_path = file_path.relative_to(output_dir)
            
            if 'executive' in file_path.name:
                title = "Executive Summary"
                description = "High-level overview of key findings and insights"
            else:
                title = file_path.stem.replace('_', ' ').title()
                description = "Analysis visualization"
            
            html_content += f"""
        <div class="viz-card">
            <h3>{title}</h3>
            <p>{description}</p>
            <a href="{relative_path}" target="_blank">View Image</a>
        </div>
"""
    
    html_content += f"""
    </div>
</body>
</html>
"""
    
    html_content = html_content.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    index_path = output_dir / "index.html"
    with open(index_path, 'w') as f:
        f.write(html_content)
    
    console.print(f"\n[green]✓[/green] Created visualization index: {index_path}")


def display_key_insights(results: Dict[str, Any]):
    """Display key insights from the analysis."""
    console.print("\n" + "="*60)
    console.print("[bold]KEY INSIGHTS FROM VISUALIZATION[/bold]")
    console.print("="*60)
    
    # Top themes across all questions
    all_themes = []
    for q_analysis in results.get('question_analyses', []):
        all_themes.extend(q_analysis.get('dominant_themes', []))
    
    # Sort by total count
    theme_counts = {}
    for theme in all_themes:
        theme_name = theme['theme']
        theme_counts[theme_name] = theme_counts.get(theme_name, 0) + theme['count']
    
    top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    console.print("\n[bold]Most Prevalent Themes:[/bold]")
    for theme, count in top_themes:
        console.print(f"• {theme}: {count} total mentions")
    
    # Urgency distribution
    high_urgency_themes = [t for t in all_themes if t.get('urgency_score', 0) > 0.7]
    console.print(f"\n[bold]High Urgency Issues:[/bold] {len(high_urgency_themes)} themes")
    
    # Program insights
    program_analyses = results.get('program_analyses', {})
    if program_analyses:
        console.print("\n[bold]Programs Analyzed:[/bold]")
        for program, data in list(program_analyses.items())[:3]:
            console.print(f"• {program}: {data.get('mention_count', 0)} mentions")
    
    console.print("\n" + "="*60)


def main():
    """Main entry point."""
    try:
        console.print(Panel.fit(
            "[bold]ACME Deep Analysis Visualization Generator[/bold]\n"
            "Creating comprehensive visualizations from GPT-4.1 analysis",
            style="bold blue"
        ))
        
        # Load results
        results = load_deep_analysis_results()
        if not results:
            sys.exit(1)
        
        # Generate visualizations
        generate_visualizations(results)
        
        console.print("\n[bold green]✓ All visualizations generated successfully![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Visualization generation interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()