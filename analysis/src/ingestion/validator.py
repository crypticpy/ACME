"""Data validation utilities with comprehensive quality checks."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel, Field

from ..config import settings
from ..validation.audit import AuditLogger


console = Console()


class ValidationResult(BaseModel):
    """Data validation result model."""
    is_valid: bool
    total_records: int
    valid_records: int
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)


class DataValidator:
    """Comprehensive data validation with audit trail."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger()
        
    def validate_all_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, ValidationResult]:
        """Validate all loaded data and return results."""
        console.print("[bold blue]Validating data quality...[/bold blue]")
        
        results = {}
        
        # Validate survey data
        results["survey"] = self._validate_survey_data(data["survey"])
        
        # Validate working document
        results["working_doc"] = self._validate_working_document(data["working_doc_main"])
        
        # Display validation summary
        self._display_validation_summary(results)
        
        # Save detailed validation report
        self._save_validation_report(results)
        
        return results
    
    def _validate_survey_data(self, df: pd.DataFrame) -> ValidationResult:
        """Validate survey data with specific business rules."""
        result = ValidationResult(
            is_valid=True,
            total_records=len(df),
            valid_records=len(df)
        )
        
        # Check for required columns (using cleaned names)
        required_cols = ['start_time', 'completion_time']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            # Not critical - just note it
            result.warnings.append(f"Some expected columns missing: {missing_cols}")
        
        # Check completion rates
        if 'completion_time' in df.columns:
            completion_rate = df['completion_time'].notna().sum() / len(df)
            result.statistics['completion_rate'] = completion_rate
            
            if completion_rate < 0.95:
                result.warnings.append(
                    f"Low completion rate: {completion_rate:.1%}"
                )
        
        # Check for duplicate responses
        if 'email' in df.columns:
            duplicate_mask = df.duplicated(subset=['email'], keep=False)
            if duplicate_mask.any():
                duplicates = df[df['email'].notna()]['email'].value_counts()
                duplicates = duplicates[duplicates > 1]
                if len(duplicates) > 0:
                    result.issues.append({
                        "type": "duplicate_responses",
                        "count": len(duplicates),
                        "severity": "warning"
                    })
        
        # Analyze response quality
        # Look for text columns that might contain responses
        text_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['what', 'describe', 'feedback', 'ideas', 'concerns']):
                text_columns.append(col)
        
        for col in text_columns[:5]:  # Limit to first 5 text columns
            if col in df.columns:
                # Check response lengths
                lengths = df[col].astype(str).str.len()
                lengths = lengths[df[col].notna()]  # Only non-null values
                
                if len(lengths) > 0:
                    short_responses = (lengths < settings.min_response_length).sum()
                    
                    if short_responses > len(df) * 0.1:
                        result.warnings.append(
                            f"High rate of short responses in question: "
                            f"{short_responses/len(df):.1%}"
                        )
                    
                    result.statistics[f"avg_response_length_{col[:30]}"] = lengths.mean()
        
        # Check geographic distribution
        zip_col = None
        for col in df.columns:
            if 'zip' in col.lower() and 'code' in col.lower():
                zip_col = col
                break
        
        if zip_col and zip_col in df.columns:
            zip_codes = df[zip_col].astype(str).str.strip()
            valid_zips = zip_codes[zip_codes.str.match(r'^\d{5}$', na=False)]
            result.statistics['unique_zip_codes'] = len(valid_zips.unique())
            result.statistics['top_5_zips'] = valid_zips.value_counts().head().to_dict()
        
        # Validate dates
        date_cols = ['start_time', 'completion_time']
        for col in date_cols:
            if col in df.columns:
                # Try to convert to datetime
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    # Check for future dates
                    future_dates = dates > pd.Timestamp.now()
                    if future_dates.any():
                        result.issues.append({
                            "type": "future_dates",
                            "column": col,
                            "count": future_dates.sum(),
                            "severity": "warning"
                        })
                except:
                    pass
        
        # Calculate data quality score
        quality_score = self._calculate_quality_score(df)
        result.statistics['quality_score'] = quality_score
        
        if quality_score < 0.8:
            result.warnings.append(
                f"Data quality score below threshold: {quality_score:.2f}"
            )
        
        # Log validation
        self.audit_logger.log_operation(
            operation="validate_survey_data",
            validation_result=result.dict(),
            quality_score=quality_score
        )
        
        return result
    
    def _validate_working_document(self, df: pd.DataFrame) -> ValidationResult:
        """Validate working document data."""
        result = ValidationResult(
            is_valid=True,
            total_records=len(df),
            valid_records=len(df)
        )
        
        # Working document likely has different structure
        # Just do basic validation
        
        # Check if it's not empty
        if len(df) == 0:
            result.issues.append({
                "type": "empty_dataset",
                "severity": "critical"
            })
            result.is_valid = False
            return result
        
        # Check for any text content
        text_cols = []
        for col in df.columns:
            sample = df[col].dropna().astype(str)
            if len(sample) > 0 and sample.str.len().mean() > 10:
                text_cols.append(col)
        
        result.statistics['text_columns'] = len(text_cols)
        result.statistics['total_columns'] = len(df.columns)
        
        # Basic quality check
        non_null_percentage = df.notna().sum().sum() / (len(df) * len(df.columns))
        result.statistics['data_density'] = non_null_percentage
        
        if non_null_percentage < 0.1:
            result.warnings.append("Very sparse data (>90% missing values)")
        
        return result
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score (0-1)."""
        scores = []
        
        # Completeness score
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        scores.append(completeness)
        
        # Consistency score (check for valid values in key columns)
        # This is simplified since we don't know exact column names
        consistency = 1.0  # Default to good
        scores.append(consistency)
        
        # Timeliness score (if we have date columns)
        timeliness = 1.0  # Default to good
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    if dates.notna().any():
                        recent_mask = dates > pd.Timestamp.now() - pd.Timedelta(days=365)
                        timeliness = recent_mask.mean()
                        break
                except:
                    pass
        scores.append(timeliness)
        
        return np.mean(scores)
    
    def _display_validation_summary(self, results: Dict[str, ValidationResult]) -> None:
        """Display validation summary in a rich table."""
        table = Table(title="Data Validation Summary", show_header=True)
        table.add_column("Dataset", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Records", justify="right")
        table.add_column("Quality Score", justify="right")
        table.add_column("Issues", justify="right")
        table.add_column("Warnings", justify="right")
        
        for name, result in results.items():
            status = "[green]✓ Valid[/green]" if result.is_valid else "[red]✗ Invalid[/red]"
            quality_score = result.statistics.get('quality_score', 0)
            
            table.add_row(
                name,
                status,
                f"{result.valid_records:,} / {result.total_records:,}",
                f"{quality_score:.2%}" if quality_score else "N/A",
                str(len(result.issues)),
                str(len(result.warnings))
            )
        
        console.print(table)
    
    def _save_validation_report(self, results: Dict[str, ValidationResult]) -> None:
        """Save detailed validation report."""
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "results": {
                name: result.dict() for name, result in results.items()
            }
        }
        
        report_file = settings.audit_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        console.print(f"[dim]Validation report saved to: {report_file}[/dim]")