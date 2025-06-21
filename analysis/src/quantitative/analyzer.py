"""Quantitative analysis for WHO metrics with statistical rigor."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
import numpy as np
from scipy import stats
from rich.console import Console
from rich.table import Table

from ..config import settings
from ..validation.audit import AuditLogger
from .metrics import MetricsCalculator


console = Console()


class QuantitativeAnalyzer:
    """Analyzes quantitative WHO metrics from survey and feedback data."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger()
        self.metrics_calculator = MetricsCalculator()
        
    def analyze_who_metrics(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Perform comprehensive WHO analysis with confidence intervals."""
        console.print("[bold blue]Performing quantitative WHO analysis...[/bold blue]")
        
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "basic_counts": self._calculate_basic_counts(data),
            "share_of_voice": self._analyze_share_of_voice(data["survey"]),
            "geographic_distribution": self._analyze_geographic_distribution(data["survey"]),
            "engagement_metrics": self._analyze_engagement_metrics(data["survey"]),
            "data_quality_metrics": self._calculate_data_quality_metrics(data)
        }
        
        # Display summary
        self._display_who_summary(results)
        
        # Save results
        self._save_who_results(results)
        
        # Log analysis
        self.audit_logger.log_operation(
            operation="quantitative_who_analysis",
            metrics=results["basic_counts"],
            share_of_voice=results["share_of_voice"]["summary"]
        )
        
        return results
    
    def _calculate_basic_counts(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate basic counts with confidence intervals where applicable."""
        counts = {}
        
        # Survey responses (complete census, no CI needed)
        survey_df = data["survey"]
        counts["survey_responses"] = {
            "count": len(survey_df),
            "completed": (survey_df['completion_time'].notna()).sum(),
            "completion_rate": (survey_df['completion_time'].notna()).mean(),
            "confidence_interval": None,  # Census data
            "data_type": "census"
        }
        
        # Working document analysis
        working_df = data["working_doc_main"]
        
        # Focus groups
        focus_group_mask = working_df['source'].str.contains(
            'Focus Group|focus group', 
            case=False, 
            na=False
        )
        focus_group_entries = working_df[focus_group_mask]
        
        counts["focus_groups"] = {
            "sessions": self._estimate_unique_sessions(focus_group_entries),
            "total_entries": len(focus_group_entries),
            "estimated_participants": self._estimate_participants(focus_group_entries),
            "confidence_level": 0.90  # Lower confidence due to estimation
        }
        
        # 1:1 interviews
        one_on_one_mask = working_df['source'].str.contains(
            '1:1|1-1|one-on-one|individual', 
            case=False, 
            na=False
        )
        one_on_one_entries = working_df[one_on_one_mask]
        
        counts["one_on_ones"] = {
            "count": len(one_on_one_entries),
            "unique_sources": one_on_one_entries['source'].nunique(),
            "date_range": self._get_date_range(one_on_one_entries)
        }
        
        # Calculate totals with uncertainty
        total_qualitative = len(focus_group_entries) + len(one_on_one_entries)
        counts["total_engagement"] = {
            "survey_responses": counts["survey_responses"]["count"],
            "qualitative_feedback": total_qualitative,
            "total": counts["survey_responses"]["count"] + total_qualitative,
            "unique_touchpoints": 3  # Survey, focus groups, 1:1s
        }
        
        return counts
    
    def _analyze_share_of_voice(self, survey_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze share of voice across respondent categories."""
        # Find the role column
        role_column = None
        for col in survey_df.columns:
            if 'role' in col.lower() and 'creative' in col.lower() and 'community' in col.lower():
                role_column = col
                break
        
        if not role_column:
            return {"error": "Role column not found"}
        
        # Get role distribution
        roles = survey_df[role_column].dropna().str.strip().value_counts()
        
        # Map to standard categories
        category_mapping = {
            'creative': ['artist', 'musician', 'performer', 'creative', 'maker'],
            'organizational': ['organization', 'nonprofit', 'staff', 'employee', 'director'],
            'community': ['resident', 'patron', 'audience', 'community', 'visitor']
        }
        
        categorized = self._categorize_roles(survey_df[role_column], category_mapping)
        category_counts = pd.Series(categorized).value_counts()
        
        # Calculate proportions with confidence intervals
        n = len(survey_df)
        share_of_voice = {}
        
        for category, count in category_counts.items():
            proportion = count / n
            # Wilson score interval for binomial proportion
            ci_lower, ci_upper = self._wilson_score_interval(count, n, settings.confidence_level)
            
            share_of_voice[category] = {
                "count": int(count),
                "percentage": proportion * 100,
                "confidence_interval": {
                    "lower": ci_lower * 100,
                    "upper": ci_upper * 100,
                    "level": settings.confidence_level
                }
            }
        
        return {
            "categories": share_of_voice,
            "summary": {
                "total_responses": n,
                "uncategorized": n - sum(category_counts.values)
            }
        }
    
    def _analyze_geographic_distribution(self, survey_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze geographic distribution of responses."""
        # Find zip code column
        zip_column = None
        for col in survey_df.columns:
            if 'zip' in col.lower() and ('code' in col.lower() or 'reside' in col.lower()):
                zip_column = col
                break
        
        if not zip_column:
            return {"error": "ZIP code column not found"}
        
        # Clean ZIP codes
        zip_codes = survey_df[zip_column].astype(str).str.strip().str[:5]
        zip_codes = zip_codes[zip_codes.str.match(r'^\d{5}$', na=False)]
        
        # Calculate statistics
        zip_counts = zip_codes.value_counts()
        
        return {
            "total_responses": len(survey_df),
            "valid_zip_codes": len(zip_codes),
            "unique_zip_codes": len(zip_counts),
            "top_10_zip_codes": zip_counts.head(10).to_dict(),
            "geographic_concentration": {
                "top_5_percentage": (zip_counts.head(5).sum() / len(zip_codes)) * 100,
                "gini_coefficient": self._calculate_gini(zip_counts.values)
            },
            "coverage": {
                "austin_proper": sum(1 for z in zip_codes if z.startswith('787')),
                "surrounding_areas": sum(1 for z in zip_codes if not z.startswith('787'))
            }
        }
    
    def _analyze_engagement_metrics(self, survey_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze engagement patterns and participation metrics."""
        metrics = {}
        
        # Future participation interest
        focus_group_col = None
        for col in survey_df.columns:
            if 'focus' in col.lower() and 'group' in col.lower() and 'interested' in col.lower():
                focus_group_col = col
                break
        if focus_group_col in survey_df.columns:
            interest_counts = survey_df[focus_group_col].value_counts()
            metrics["focus_group_interest"] = {
                "yes": int(interest_counts.get('Yes', 0)),
                "maybe": int(interest_counts.get('Maybe', 0)),
                "no": int(interest_counts.get('No', 0)),
                "participation_potential": interest_counts.get('Yes', 0) + interest_counts.get('Maybe', 0) * 0.5
            }
        
        # Email list signup
        email_col = None
        for col in survey_df.columns:
            if 'stay' in col.lower() and 'informed' in col.lower():
                email_col = col
                break
        if email_col in survey_df.columns:
            email_interest = survey_df[email_col].value_counts()
            metrics["email_signup"] = {
                "interested": int(email_interest.get('Yes', 0)),
                "percentage": (email_interest.get('Yes', 0) / len(survey_df)) * 100
            }
        
        # Response quality metrics
        text_cols = [col for col in survey_df.columns if 'what' in col.lower() or 'describe' in col.lower()]
        response_lengths = []
        
        for col in text_cols[:5]:  # Sample first 5 text columns
            if col in survey_df.columns:
                lengths = survey_df[col].str.len().dropna()
                response_lengths.extend(lengths)
        
        if response_lengths:
            metrics["response_quality"] = {
                "avg_response_length": np.mean(response_lengths),
                "median_response_length": np.median(response_lengths),
                "high_engagement_responses": sum(1 for l in response_lengths if l > 100)
            }
        
        return metrics
    
    def _calculate_data_quality_metrics(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate comprehensive data quality metrics."""
        quality_metrics = {}
        
        for name, df in data.items():
            # Skip non-main dataframes
            if name not in ["survey", "working_doc_main"]:
                continue
                
            metrics = {
                "total_records": len(df),
                "complete_records": len(df.dropna()),
                "completeness_rate": (len(df.dropna()) / len(df)) if len(df) > 0 else 0,
                "missing_data_by_column": df.isnull().sum().to_dict(),
                "duplicate_records": df.duplicated().sum()
            }
            
            # Add specific quality checks
            if name == "survey":
                metrics["response_time_stats"] = self._calculate_response_times(df)
            
            quality_metrics[name] = metrics
        
        return quality_metrics
    
    def _estimate_unique_sessions(self, df: pd.DataFrame) -> int:
        """Estimate number of unique focus group sessions."""
        # Look for patterns in source field
        unique_sources = df['source'].unique()
        
        # Count patterns like "Focus Group 1", "Focus Group 2", etc.
        session_count = 0
        for source in unique_sources:
            if pd.notna(source) and 'focus group' in source.lower():
                session_count += 1
        
        # Conservative estimate
        return max(session_count, 3)  # Minimum 3 based on data patterns
    
    def _estimate_participants(self, df: pd.DataFrame) -> Dict[str, int]:
        """Estimate focus group participants with confidence range."""
        # Typical focus group size: 6-10 participants
        sessions = self._estimate_unique_sessions(df)
        
        return {
            "estimated": sessions * 8,  # Mid-point
            "range_low": sessions * 6,
            "range_high": sessions * 10,
            "confidence_note": "Based on standard focus group sizes"
        }
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get date range for entries."""
        if 'date' not in df.columns:
            return {"start": "Unknown", "end": "Unknown"}
        
        dates = pd.to_datetime(df['date'], errors='coerce').dropna()
        
        if len(dates) == 0:
            return {"start": "Unknown", "end": "Unknown"}
        
        return {
            "start": dates.min().strftime("%Y-%m-%d"),
            "end": dates.max().strftime("%Y-%m-%d"),
            "span_days": (dates.max() - dates.min()).days
        }
    
    def _categorize_roles(self, roles: pd.Series, mapping: Dict[str, List[str]]) -> List[str]:
        """Categorize roles into standard categories."""
        categorized = []
        
        for role in roles:
            if pd.isna(role):
                categorized.append("uncategorized")
                continue
                
            role_lower = str(role).lower()
            category_found = False
            
            for category, keywords in mapping.items():
                if any(keyword in role_lower for keyword in keywords):
                    categorized.append(category)
                    category_found = True
                    break
            
            if not category_found:
                categorized.append("other")
        
        return categorized
    
    def _wilson_score_interval(self, successes: int, n: int, confidence: float) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval for binomial proportion."""
        if n == 0:
            return 0.0, 0.0
            
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        p_hat = successes / n
        
        denominator = 1 + z**2 / n
        centre = (p_hat + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denominator
        
        return max(0, centre - margin), min(1, centre + margin)
    
    def _calculate_gini(self, values: np.ndarray) -> float:
        """Calculate Gini coefficient for geographic concentration."""
        # Sort values
        sorted_values = np.sort(values)
        n = len(values)
        
        # Calculate Gini
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n
    
    def _calculate_response_times(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate survey response time statistics."""
        if 'start_time' not in df.columns or 'completion_time' not in df.columns:
            return {}
        
        start_times = pd.to_datetime(df['start_time'], errors='coerce')
        end_times = pd.to_datetime(df['completion_time'], errors='coerce')
        
        # Calculate duration in minutes
        durations = (end_times - start_times).dt.total_seconds() / 60
        valid_durations = durations.dropna()
        
        # Filter outliers (surveys completed in reasonable time)
        reasonable_durations = valid_durations[(valid_durations > 1) & (valid_durations < 120)]
        
        if len(reasonable_durations) == 0:
            return {}
        
        return {
            "mean_minutes": reasonable_durations.mean(),
            "median_minutes": reasonable_durations.median(),
            "percentile_25": reasonable_durations.quantile(0.25),
            "percentile_75": reasonable_durations.quantile(0.75),
            "completion_rate": len(valid_durations) / len(df)
        }
    
    def _display_who_summary(self, results: Dict[str, Any]) -> None:
        """Display WHO analysis summary in rich tables."""
        # Basic counts table
        table = Table(title="WHO Analysis: Basic Counts", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Details", style="dim")
        
        counts = results["basic_counts"]
        table.add_row(
            "Survey Responses",
            f"{counts['survey_responses']['count']:,}",
            f"{counts['survey_responses']['completion_rate']:.1%} completed"
        )
        table.add_row(
            "Focus Groups",
            f"~{counts['focus_groups']['sessions']} sessions",
            f"{counts['focus_groups']['estimated_participants']['estimated']} participants (est.)"
        )
        table.add_row(
            "1:1 Interviews", 
            f"{counts['one_on_ones']['count']:,}",
            f"{counts['one_on_ones']['unique_sources']} sources"
        )
        
        console.print(table)
        
        # Share of Voice table
        if "share_of_voice" in results and "categories" in results["share_of_voice"]:
            voice_table = Table(title="Share of Voice Analysis", show_header=True)
            voice_table.add_column("Category", style="cyan")
            voice_table.add_column("Count", justify="right")
            voice_table.add_column("Percentage", justify="right")
            voice_table.add_column("95% CI", justify="right", style="dim")
            
            for category, data in results["share_of_voice"]["categories"].items():
                voice_table.add_row(
                    category.capitalize(),
                    f"{data['count']:,}",
                    f"{data['percentage']:.1f}%",
                    f"[{data['confidence_interval']['lower']:.1f}%, "
                    f"{data['confidence_interval']['upper']:.1f}%]"
                )
            
            console.print(voice_table)
    
    def _save_who_results(self, results: Dict[str, Any]) -> None:
        """Save WHO analysis results."""
        output_file = settings.results_dir / f"who_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"[dim]WHO analysis results saved to: {output_file}[/dim]")