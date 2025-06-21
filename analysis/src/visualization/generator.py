"""Main visualization generator for creating all analysis charts."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from rich.console import Console

from ..config import settings
from ..validation.audit import AuditLogger
from .charts import (
    ShareOfVoiceChart,
    ThemeChart,
    ProgramAnalysisChart,
    GeographicChart,
    ConfidenceIntervalChart
)

console = Console()


class VisualizationGenerator:
    """Generates all visualizations for the analysis."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger()
        self.output_dir = settings.results_dir / "visualizations"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        # Chart generators
        self.share_of_voice_chart = ShareOfVoiceChart()
        self.theme_chart = ThemeChart()
        self.program_chart = ProgramAnalysisChart()
        self.geographic_chart = GeographicChart()
        self.confidence_chart = ConfidenceIntervalChart()
    
    def generate_all_visualizations(
        self,
        quantitative_results: Dict[str, Any],
        qualitative_results: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate all visualizations from analysis results."""
        console.print("[bold blue]Generating visualizations...[/bold blue]")
        
        generated_files = {
            "static": [],
            "interactive": [],
            "data_exports": []
        }
        
        try:
            # 1. Share of Voice visualizations
            console.print("[dim]Creating share of voice charts...[/dim]")
            sov_files = self._generate_share_of_voice_charts(
                quantitative_results.get("share_of_voice", {}),
                qualitative_results.get("share_of_voice_refined", {})
            )
            generated_files["static"].extend(sov_files.get("static", []))
            generated_files["interactive"].extend(sov_files.get("interactive", []))
            
            # 2. Theme visualizations
            console.print("[dim]Creating theme analysis charts...[/dim]")
            theme_files = self._generate_theme_charts(
                qualitative_results.get("major_themes", [])
            )
            generated_files["static"].extend(theme_files.get("static", []))
            generated_files["interactive"].extend(theme_files.get("interactive", []))
            
            # 3. Program analysis visualizations
            console.print("[dim]Creating program analysis charts...[/dim]")
            program_files = self._generate_program_charts(
                qualitative_results.get("program_analysis", {})
            )
            generated_files["static"].extend(program_files.get("static", []))
            generated_files["interactive"].extend(program_files.get("interactive", []))
            
            # 4. Geographic visualizations
            console.print("[dim]Creating geographic distribution charts...[/dim]")
            geo_files = self._generate_geographic_charts(
                quantitative_results.get("geographic_distribution", {})
            )
            generated_files["static"].extend(geo_files.get("static", []))
            generated_files["interactive"].extend(geo_files.get("interactive", []))
            
            # 5. Statistical confidence visualizations
            console.print("[dim]Creating statistical confidence charts...[/dim]")
            conf_files = self._generate_confidence_charts(quantitative_results)
            generated_files["static"].extend(conf_files.get("static", []))
            
            # 6. Export data for microsite
            console.print("[dim]Exporting data for microsite...[/dim]")
            export_files = self._export_visualization_data(
                quantitative_results,
                qualitative_results
            )
            generated_files["data_exports"].extend(export_files)
            
            # Log completion
            self.audit_logger.log_operation(
                operation="visualization_generation_complete",
                charts_generated={
                    "static": len(generated_files["static"]),
                    "interactive": len(generated_files["interactive"]),
                    "exports": len(generated_files["data_exports"])
                }
            )
            
            console.print(f"[green]Generated {sum(len(v) for v in generated_files.values())} visualization files[/green]")
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="visualization_generation",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"error": str(e)}
            )
            console.print(f"[red]Error generating visualizations: {e}[/red]")
            
        return generated_files
    
    def _generate_share_of_voice_charts(
        self,
        basic_sov: Dict[str, Any],
        refined_sov: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate share of voice visualizations."""
        files = {"static": [], "interactive": []}
        
        # Basic share of voice pie chart
        if basic_sov:
            static_file = self.share_of_voice_chart.create_pie_chart(
                basic_sov,
                self.output_dir / "share_of_voice_basic.png"
            )
            files["static"].append(str(static_file))
        
        # Refined share of voice with confidence
        if refined_sov.get("refined_categories"):
            # Static version
            static_file = self.share_of_voice_chart.create_refined_chart(
                refined_sov["refined_categories"],
                self.output_dir / "share_of_voice_refined.png"
            )
            files["static"].append(str(static_file))
            
            # Interactive version
            interactive_file = self.share_of_voice_chart.create_interactive_chart(
                refined_sov["refined_categories"],
                self.output_dir / "share_of_voice_interactive.html"
            )
            files["interactive"].append(str(interactive_file))
        
        return files
    
    def _generate_theme_charts(self, themes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate theme analysis visualizations."""
        files = {"static": [], "interactive": []}
        
        if not themes:
            return files
        
        # Top themes bar chart
        static_file = self.theme_chart.create_theme_bar_chart(
            themes[:10],
            self.output_dir / "top_themes.png"
        )
        files["static"].append(str(static_file))
        
        # Theme sentiment distribution
        static_file = self.theme_chart.create_sentiment_distribution(
            themes,
            self.output_dir / "theme_sentiments.png"
        )
        files["static"].append(str(static_file))
        
        # Interactive theme explorer
        interactive_file = self.theme_chart.create_interactive_theme_explorer(
            themes,
            self.output_dir / "theme_explorer.html"
        )
        files["interactive"].append(str(interactive_file))
        
        # Theme word cloud
        static_file = self.theme_chart.create_theme_word_cloud(
            themes,
            self.output_dir / "theme_wordcloud.png"
        )
        files["static"].append(str(static_file))
        
        return files
    
    def _generate_program_charts(self, program_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate program-specific visualizations."""
        files = {"static": [], "interactive": []}
        
        if not program_data:
            return files
        
        # Program comparison chart
        static_file = self.program_chart.create_program_comparison(
            program_data,
            self.output_dir / "program_comparison.png"
        )
        files["static"].append(str(static_file))
        
        # Interactive program dashboard
        interactive_file = self.program_chart.create_program_dashboard(
            program_data,
            self.output_dir / "program_dashboard.html"
        )
        files["interactive"].append(str(interactive_file))
        
        # Individual program reports
        for program_name, data in program_data.items():
            if data.get("themes"):
                static_file = self.program_chart.create_program_detail_chart(
                    program_name,
                    data,
                    self.output_dir / f"program_{program_name.lower().replace(' ', '_')}.png"
                )
                files["static"].append(str(static_file))
        
        return files
    
    def _generate_geographic_charts(self, geo_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate geographic distribution visualizations."""
        files = {"static": [], "interactive": []}
        
        if not geo_data or not geo_data.get("zip_codes"):
            return files
        
        # Static choropleth map
        static_file = self.geographic_chart.create_zip_code_map(
            geo_data["zip_codes"],
            self.output_dir / "geographic_distribution.png"
        )
        files["static"].append(str(static_file))
        
        # Interactive map
        interactive_file = self.geographic_chart.create_interactive_map(
            geo_data["zip_codes"],
            self.output_dir / "geographic_interactive.html"
        )
        files["interactive"].append(str(interactive_file))
        
        return files
    
    def _generate_confidence_charts(self, quant_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate statistical confidence visualizations."""
        files = {"static": []}
        
        # Confidence intervals for key metrics
        if quant_results.get("share_of_voice"):
            static_file = self.confidence_chart.create_confidence_interval_chart(
                quant_results["share_of_voice"],
                self.output_dir / "confidence_intervals.png"
            )
            files["static"].append(str(static_file))
        
        # Statistical summary dashboard
        static_file = self.confidence_chart.create_statistical_summary(
            quant_results,
            self.output_dir / "statistical_summary.png"
        )
        files["static"].append(str(static_file))
        
        return files
    
    def _export_visualization_data(
        self,
        quantitative_results: Dict[str, Any],
        qualitative_results: Dict[str, Any]
    ) -> List[str]:
        """Export processed data for microsite consumption."""
        export_files = []
        
        # Combined data export
        combined_data = {
            "generated_at": datetime.now().isoformat(),
            "quantitative": quantitative_results,
            "qualitative": qualitative_results,
            "metadata": {
                "total_responses": quantitative_results.get("total_responses", 0),
                "analysis_version": "2.0",
                "model_used": settings.openai_model
            }
        }
        
        # Main data export
        export_file = self.output_dir / "analysis_data.json"
        with open(export_file, 'w') as f:
            json.dump(combined_data, f, indent=2, default=str)
        export_files.append(str(export_file))
        
        # Microsite-specific exports
        microsite_data = self._prepare_microsite_data(
            quantitative_results,
            qualitative_results
        )
        
        microsite_file = self.output_dir / "microsite_data.json"
        with open(microsite_file, 'w') as f:
            json.dump(microsite_data, f, indent=2)
        export_files.append(str(microsite_file))
        
        return export_files
    
    def _prepare_microsite_data(
        self,
        quantitative_results: Dict[str, Any],
        qualitative_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data specifically formatted for microsite consumption."""
        return {
            "summary": {
                "totalResponses": quantitative_results.get("total_responses", 0),
                "responseRate": quantitative_results.get("response_rate", 0),
                "lastUpdated": datetime.now().isoformat()
            },
            "shareOfVoice": {
                "categories": [
                    {
                        "name": category,
                        "value": data.get("count", 0),
                        "percentage": data.get("percentage", 0),
                        "confidence": data.get("average_confidence", 0)
                    }
                    for category, data in qualitative_results.get(
                        "share_of_voice_refined", {}
                    ).get("refined_categories", {}).items()
                ]
            },
            "themes": [
                {
                    "id": f"theme_{i}",
                    "name": theme.get("theme", ""),
                    "count": theme.get("count", 0),
                    "percentage": theme.get("percentage", 0),
                    "description": theme.get("description", ""),
                    "sentiment": theme.get("sentiment", "neutral"),
                    "urgency": theme.get("urgency", "medium"),
                    "keywords": theme.get("keywords", [])
                }
                for i, theme in enumerate(
                    qualitative_results.get("major_themes", [])[:10]
                )
            ],
            "programs": [
                {
                    "name": program,
                    "responseCount": data.get("response_count", 0),
                    "themes": [
                        {
                            "theme": t.get("theme", ""),
                            "sentiment": t.get("sentiment", "neutral"),
                            "frequency": t.get("frequency", 0)
                        }
                        for t in data.get("themes", [])[:3]
                    ]
                }
                for program, data in qualitative_results.get(
                    "program_analysis", {}
                ).items()
            ],
            "geographic": {
                "zipCodes": [
                    {
                        "zipCode": zip_code,
                        "count": count,
                        "percentage": (count / quantitative_results.get("total_responses", 1)) * 100
                    }
                    for zip_code, count in quantitative_results.get(
                        "geographic_distribution", {}
                    ).get("zip_codes", {}).items()
                ]
            }
        }