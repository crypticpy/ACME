"""Configuration settings for the analysis pipeline."""

import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    env: str = Field(default="development", env="ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Keys - Azure OpenAI
    azure_openai_endpoint: str = Field(default="", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="", env="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: str = Field(default="gpt-4-1", env="AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Legacy OpenAI settings (kept for backwards compatibility)
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1", env="OPENAI_MODEL")
    embedding_model: str = Field(default="text-embedding-3-large", env="EMBEDDING_MODEL")
    
    # File Paths
    project_root: Path = Path(__file__).parent.parent.parent
    analysis_root: Path = Path(__file__).parent.parent
    data_dir: Optional[Path] = None
    raw_data_dir: Optional[Path] = None
    processed_data_dir: Optional[Path] = None
    results_dir: Optional[Path] = None
    audit_dir: Optional[Path] = None
    
    # Analysis Parameters
    confidence_level: float = Field(default=0.95, env="CONFIDENCE_LEVEL")
    min_theme_frequency: int = Field(default=10, env="MIN_THEME_FREQUENCY")
    max_themes: int = Field(default=10, env="MAX_THEMES")
    
    # Program Names
    programs: List[str] = Field(
        default=[
            "Nexus",
            "Thrive", 
            "Elevate",
            "Austin Live Music Fund",
            "Art in Public Places",
            "Creative Space Assistance Program"
        ]
    )
    
    # Data Quality Thresholds
    max_missing_rate: float = Field(default=0.1, env="MAX_MISSING_RATE")
    min_response_length: int = Field(default=10, env="MIN_RESPONSE_LENGTH")
    
    # LLM Parameters
    llm_temperature: float = Field(default=0.3, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    llm_retry_attempts: int = Field(default=3, env="LLM_RETRY_ATTEMPTS")
    
    # Visualization Settings
    color_palette: Dict[str, str] = Field(
        default={
            "primary": "#1a365d",
            "secondary": "#e53e3e", 
            "accent": "#38b2ac",
            "success": "#48bb78",
            "warning": "#ed8936",
            "info": "#4299e1",
            "neutral": "#718096"
        }
    )
    
    # Report Settings
    report_title: str = Field(
        default="ACME Cultural Funding Analysis 2025",
        env="REPORT_TITLE"
    )
    report_author: str = Field(
        default="ACME Data Science Team",
        env="REPORT_AUTHOR"
    )
    
    def __init__(self, **kwargs):
        """Initialize settings with computed fields."""
        super().__init__(**kwargs)
        
        # Set up directory paths
        if self.data_dir is None:
            self.data_dir = self.analysis_root / "data"
        if self.raw_data_dir is None:
            self.raw_data_dir = self.data_dir / "raw"
        if self.processed_data_dir is None:
            self.processed_data_dir = self.data_dir / "processed"
        if self.results_dir is None:
            self.results_dir = self.data_dir / "results"
        if self.audit_dir is None:
            self.audit_dir = self.data_dir / "audit"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields
    }


# Create global settings instance
# Load from environment
settings = Settings()