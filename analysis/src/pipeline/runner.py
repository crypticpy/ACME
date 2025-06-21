"""Main analysis pipeline runner."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import settings
from ..ingestion import DataLoader, DataValidator
from ..quantitative import QuantitativeAnalyzer
from ..qualitative import QualitativeAnalyzer
from ..validation import AuditLogger
from ..visualization import VisualizationGenerator
from ..reporting import ReportGenerator


console = Console()
app = typer.Typer()


class AnalysisPipeline:
    """Orchestrates the complete analysis pipeline."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.audit_logger = AuditLogger(session_id=self.session_id)
        self.data = {}
        self.results = {}
        
    def run(self) -> Dict[str, Any]:
        """Run the complete analysis pipeline."""
        console.print(
            Panel.fit(
                f"[bold blue]ACME Cultural Funding Analysis Pipeline[/bold blue]\n"
                f"Session ID: {self.session_id}",
                border_style="blue"
            )
        )
        
        try:
            # Step 1: Load data
            self._load_data()
            
            # Step 2: Validate data
            self._validate_data()
            
            # Step 3: Quantitative analysis
            self._run_quantitative_analysis()
            
            # Step 4: Qualitative analysis
            self._run_qualitative_analysis()
            
            # Step 5: Generate visualizations
            self._generate_visualizations()
            
            # Step 6: Generate executive report
            self._generate_report()
            
            # Step 7: Save results
            self._save_results()
            
            # Step 8: Generate lineage report
            self._generate_lineage_report()
            
            console.print(
                Panel.fit(
                    "[bold green]✓ Analysis pipeline completed successfully![/bold green]",
                    border_style="green"
                )
            )
            
            return self.results
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="pipeline_run",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"step": "unknown"}
            )
            console.print(f"[bold red]Error: {e}[/bold red]")
            raise
        finally:
            self.audit_logger.close()
    
    def _load_data(self) -> None:
        """Load all data files."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading data files...", total=None)
            
            loader = DataLoader(self.audit_logger)
            self.data = loader.load_all_data()
            
            progress.update(task, completed=True)
    
    def _validate_data(self) -> None:
        """Validate loaded data."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating data quality...", total=None)
            
            validator = DataValidator(self.audit_logger)
            validation_results = validator.validate_all_data(self.data)
            
            # Check if all data is valid
            all_valid = all(result.is_valid for result in validation_results.values())
            
            if not all_valid:
                console.print("[bold red]Data validation failed![/bold red]")
                # In production, might want to halt pipeline here
            
            self.results["validation"] = validation_results
            progress.update(task, completed=True)
    
    def _run_quantitative_analysis(self) -> None:
        """Run quantitative WHO analysis."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running quantitative analysis...", total=None)
            
            analyzer = QuantitativeAnalyzer(self.audit_logger)
            who_results = analyzer.analyze_who_metrics(self.data)
            
            self.results["quantitative"] = who_results
            progress.update(task, completed=True)
    
    def _run_qualitative_analysis(self) -> None:
        """Run qualitative WHAT analysis."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running qualitative analysis...", total=None)
            
            analyzer = QualitativeAnalyzer(self.audit_logger)
            what_results = analyzer.analyze_what_themes(self.data)
            
            self.results["qualitative"] = what_results
            progress.update(task, completed=True)
    
    def _generate_visualizations(self) -> None:
        """Generate all visualizations."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating visualizations...", total=None)
            
            viz_gen = VisualizationGenerator(self.audit_logger)
            viz_files = viz_gen.generate_all_visualizations(
                self.results.get("quantitative", {}),
                self.results.get("qualitative", {})
            )
            
            self.results["visualizations"] = viz_files
            progress.update(task, completed=True)
    
    def _generate_report(self) -> None:
        """Generate executive report."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating executive report...", total=None)
            
            report_gen = ReportGenerator(self.audit_logger)
            report_path = report_gen.generate_executive_report(
                self.results,
                self.results.get("visualizations", {})
            )
            
            self.results["report_path"] = str(report_path)
            progress.update(task, completed=True)
    
    def _save_results(self) -> None:
        """Save all results to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory for this session
        session_dir = settings.results_dir / f"session_{self.session_id}"
        session_dir.mkdir(exist_ok=True, parents=True)
        
        # Save main results file
        import json
        results_file = session_dir / f"analysis_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        console.print(f"[dim]Results saved to: {results_file}[/dim]")
    
    def _generate_lineage_report(self) -> None:
        """Generate data lineage report."""
        lineage_file = settings.audit_dir / f"lineage_report_{self.session_id}.json"
        lineage = self.audit_logger.create_lineage_report(lineage_file)
        
        console.print(f"[dim]Lineage report saved to: {lineage_file}[/dim]")
        console.print(f"[dim]Total operations: {lineage['operations']}[/dim]")


@app.command()
def run_analysis(
    session_id: Optional[str] = typer.Option(None, help="Custom session ID"),
    skip_validation: bool = typer.Option(False, help="Skip data validation"),
):
    """Run the ACME cultural funding analysis pipeline."""
    pipeline = AnalysisPipeline(session_id=session_id)
    
    try:
        results = pipeline.run()
        console.print("[bold green]Analysis completed successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Pipeline failed: {e}[/bold red]")
        sys.exit(1)


@app.command()
def validate_data():
    """Validate data files without running full analysis."""
    console.print("[bold blue]Validating data files...[/bold blue]")
    
    audit_logger = AuditLogger()
    
    # Load data
    loader = DataLoader(audit_logger)
    data = loader.load_all_data()
    
    # Validate
    validator = DataValidator(audit_logger)
    results = validator.validate_all_data(data)
    
    # Summary
    all_valid = all(result.is_valid for result in results.values())
    
    if all_valid:
        console.print("[bold green]✓ All data validation passed![/bold green]")
    else:
        console.print("[bold red]✗ Data validation failed![/bold red]")
        
    audit_logger.close()


@app.command()
def check_config():
    """Check configuration and environment setup."""
    console.print("[bold blue]Configuration Check[/bold blue]\n")
    
    # Check API key
    if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
        console.print("[green]✓[/green] OpenAI API key configured")
    else:
        console.print("[red]✗[/red] OpenAI API key not configured")
    
    # Check directories
    dirs_to_check = [
        ("Data directory", settings.data_dir),
        ("Raw data", settings.raw_data_dir),
        ("Processed data", settings.processed_data_dir),
        ("Results", settings.results_dir),
        ("Audit logs", settings.audit_dir)
    ]
    
    for name, path in dirs_to_check:
        if path.exists():
            console.print(f"[green]✓[/green] {name}: {path}")
        else:
            console.print(f"[yellow]![/yellow] {name}: {path} (will be created)")
    
    # Check data files
    console.print("\n[bold]Data Files:[/bold]")
    
    survey_file = settings.project_root.parent / "NEW_Data" / "ACME Community Survey_ Arts, Culture, Music & Entertainment in Austin (1-1244.xlsx"
    working_file = settings.project_root.parent / "NEW_Data" / "ACME Win Win_ Working Document_TEAM WORKING DOC.xlsx"
    
    for name, path in [("Survey data", survey_file), ("Working document", working_file)]:
        if path.exists():
            console.print(f"[green]✓[/green] {name}: Found")
        else:
            console.print(f"[red]✗[/red] {name}: Not found at {path}")


if __name__ == "__main__":
    app()