#!/usr/bin/env python3
"""Run visualization and report generation using existing analysis results."""

import json
from pathlib import Path
from datetime import datetime
from rich.console import Console

from src.visualization.generator import VisualizationGenerator
from src.reporting.generator import ReportGenerator
from src.validation.audit import AuditLogger

console = Console()

def load_latest_results():
    """Load the most recent analysis results."""
    results_dir = Path("data/results")
    
    # Find latest WHO and WHAT analysis files
    who_files = sorted(results_dir.glob("who_analysis_*.json"))
    what_files = sorted(results_dir.glob("what_analysis_*.json"))
    
    if not who_files or not what_files:
        raise FileNotFoundError("No analysis results found")
    
    # Load the latest files
    with open(who_files[-1]) as f:
        who_results = json.load(f)
    
    with open(what_files[-1]) as f:
        what_results = json.load(f)
    
    console.print(f"[green]Loaded WHO results from: {who_files[-1].name}[/]")
    console.print(f"[green]Loaded WHAT results from: {what_files[-1].name}[/]")
    
    return who_results, what_results

def main():
    """Run visualization and report generation."""
    console.print("[bold blue]ACME Visualization and Report Generator[/]")
    
    try:
        # Load analysis results
        who_results, what_results = load_latest_results()
        
        # Initialize components
        audit_logger = AuditLogger()
        viz_generator = VisualizationGenerator(audit_logger)
        report_generator = ReportGenerator(audit_logger)
        
        # Generate visualizations
        console.print("\n[yellow]Generating visualizations...[/]")
        visualizations = viz_generator.generate_all_visualizations(
            quantitative_results=who_results,
            qualitative_results=what_results
        )
        
        # Generate report
        console.print("\n[yellow]Generating executive report...[/]")
        combined_results = {
            "quantitative": who_results,
            "qualitative": what_results,
            "timestamp": datetime.now().isoformat()
        }
        
        report_path = report_generator.generate_executive_report(
            results=combined_results,
            visualizations=visualizations
        )
        
        console.print(f"\n[green]✓ Report generated: {report_path}[/]")
        
        # Export data for microsite
        console.print("\n[yellow]Exporting data for microsite...[/]")
        export_path = Path("data/results/analysis_data.json")
        
        export_data = {
            "summary": {
                "totalResponses": who_results["basic_counts"]["survey_responses"]["count"],
                "responseRate": 100.0,  # Survey completion rate
                "confidenceLevel": 95,
                "lastUpdated": datetime.now().isoformat()
            },
            "shareOfVoice": who_results["share_of_voice"],
            "themes": what_results.get("themes", []),
            "programs": what_results.get("program_insights", []),
            "geographic": who_results.get("geographic_distribution", {})
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        console.print(f"[green]✓ Data exported to: {export_path}[/]")
        
        # Copy to microsite
        microsite_data = Path("../microsite/public/data")
        microsite_data.mkdir(exist_ok=True, parents=True)
        
        import shutil
        shutil.copy2(export_path, microsite_data / "analysis_data.json")
        console.print(f"[green]✓ Data copied to microsite[/]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        raise

if __name__ == "__main__":
    main()