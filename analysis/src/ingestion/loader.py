"""Data loading utilities for Excel files."""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
from rich.console import Console
from rich.progress import track

from ..config import settings
from ..validation.audit import AuditLogger


console = Console()


class DataLoader:
    """Handles loading and initial processing of Excel data files."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger()
        # Simplified filenames - we'll look for files containing these patterns
        self.survey_pattern = "ACME_Community_Survey"
        self.working_doc_pattern = "ACME_Working_Document"
        
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all data files and return processed DataFrames."""
        console.print("[bold blue]Loading data files...[/bold blue]")
        
        # Load survey data
        survey_df = self._load_survey_data()
        
        # Load working document data
        working_doc_dfs = self._load_working_document()
        
        # Create comprehensive data dictionary
        data = {
            "survey": survey_df,
            "working_doc_main": working_doc_dfs["Database"],
            "working_doc_guide": working_doc_dfs["Guide"],
            "working_doc_aipp": working_doc_dfs["AIPP Test"]
        }
        
        # Log summary statistics
        self._log_data_summary(data)
        
        console.print("[bold green]✓ All data loaded successfully![/bold green]")
        return data
    
    def _load_survey_data(self) -> pd.DataFrame:
        """Load and process the community survey data."""
        # Find the survey file
        file_path = None
        
        # First check raw data directory
        console.print(f"[dim]Looking for survey file in: {settings.raw_data_dir}[/dim]")
        for file in settings.raw_data_dir.glob("*.xlsx"):
            console.print(f"[dim]Found file: {file.name}[/dim]")
            if self.survey_pattern in file.name:
                file_path = file
                console.print(f"[green]Matched survey file: {file.name}[/green]")
                break
        
        # If not found, check NEW_Data folder
        if not file_path:
            new_data_dir = settings.project_root.parent.parent.parent / "NEW_Data"
            for file in new_data_dir.glob("*.xlsx"):
                if self.survey_pattern in file.name:
                    # Copy to raw data directory
                    import shutil
                    dest_path = settings.raw_data_dir / file.name
                    shutil.copy2(file, dest_path)
                    file_path = dest_path
                    console.print(f"[yellow]Copied survey file to raw data directory[/yellow]")
                    break
        
        if not file_path:
            raise FileNotFoundError(f"Survey file not found with pattern: {self.survey_pattern}")
        
        # Load Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Standardize column names
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # Add metadata
        df['source_file'] = file_path.name
        df['load_timestamp'] = datetime.now()
        df['record_type'] = 'survey'
        
        # Generate unique IDs for traceability
        df['record_id'] = df.apply(
            lambda row: self._generate_record_id('survey', row.name), axis=1
        )
        
        # Log the operation
        self.audit_logger.log_operation(
            operation="load_survey_data",
            input_file=str(file_path),
            output_shape=df.shape,
            columns=[str(col) for col in df.columns],
            data_hash=self._hash_dataframe(df)
        )
        
        return df
    
    def _load_working_document(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from the working document."""
        # Find the working document file
        file_path = None
        
        # First check raw data directory
        for file in settings.raw_data_dir.glob("*.xlsx"):
            if self.working_doc_pattern in file.name:
                file_path = file
                break
        
        # If not found, check NEW_Data folder
        if not file_path:
            new_data_dir = settings.project_root.parent.parent.parent / "NEW_Data"
            for file in new_data_dir.glob("*.xlsx"):
                if self.working_doc_pattern in file.name:
                    # Copy to raw data directory
                    import shutil
                    dest_path = settings.raw_data_dir / file.name
                    shutil.copy2(file, dest_path)
                    file_path = dest_path
                    console.print(f"[yellow]Copied working document to raw data directory[/yellow]")
                    break
        
        if not file_path:
            raise FileNotFoundError(f"Working document not found with pattern: {self.working_doc_pattern}")
        
        # Load all sheets
        xl_file = pd.ExcelFile(file_path, engine='openpyxl')
        dfs = {}
        
        for sheet_name in xl_file.sheet_names:
            if sheet_name != "Template - Do Not Delete":
                df = pd.read_excel(xl_file, sheet_name=sheet_name)
                
                # Standardize column names
                df.columns = [self._clean_column_name(col) for col in df.columns]
                
                # Add metadata
                df['source_file'] = file_path.name
                df['source_sheet'] = sheet_name
                df['load_timestamp'] = datetime.now()
                
                # Generate unique IDs
                df['record_id'] = df.apply(
                    lambda row: self._generate_record_id(f'wd_{sheet_name}', row.name), 
                    axis=1
                )
                
                dfs[sheet_name] = df
                
                # Log the operation
                self.audit_logger.log_operation(
                    operation=f"load_working_doc_{sheet_name}",
                    input_file=str(file_path),
                    sheet_name=sheet_name,
                    output_shape=df.shape,
                    columns=[str(col) for col in df.columns],
                    data_hash=self._hash_dataframe(df)
                )
        
        return dfs
    
    def _clean_column_name(self, col_name: str) -> str:
        """Standardize column names for consistency."""
        import re
        # Convert to lowercase, replace spaces with underscores
        clean_name = str(col_name).lower().strip()
        clean_name = re.sub(r'[^\w\s]', '', clean_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        return clean_name
    
    def _generate_record_id(self, prefix: str, index: int) -> str:
        """Generate a unique, traceable record ID."""
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{prefix}_{timestamp}_{index:06d}"
    
    def _hash_dataframe(self, df: pd.DataFrame) -> str:
        """Generate a hash of the dataframe for audit purposes."""
        # Convert dataframe to string representation
        df_str = df.to_json(orient='records', date_format='iso')
        # Generate SHA256 hash
        return hashlib.sha256(df_str.encode()).hexdigest()[:16]
    
    def _log_data_summary(self, data: Dict[str, pd.DataFrame]) -> None:
        """Log summary statistics for all loaded data."""
        summary = {
            "load_timestamp": datetime.now().isoformat(),
            "data_sources": {}
        }
        
        for name, df in data.items():
            summary["data_sources"][name] = {
                "shape": df.shape,
                "columns": len(df.columns),
                "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                "dtypes": {str(k): v for k, v in df.dtypes.value_counts().to_dict().items()}
            }
        
        # Save summary to audit directory
        summary_file = settings.audit_dir / f"data_load_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        console.print(f"[dim]Data summary saved to: {summary_file}[/dim]")