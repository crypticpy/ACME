"""ACME Cultural Funding Analysis Pipeline."""

__version__ = "1.0.0"
__author__ = "ACME Data Science Team"

from .ingestion import DataLoader, DataValidator
from .quantitative import QuantitativeAnalyzer
from .qualitative import QualitativeAnalyzer
from .validation import AuditLogger
from .visualization import VisualizationGenerator
from .reporting import ReportGenerator

__all__ = [
    'DataLoader',
    'DataValidator', 
    'QuantitativeAnalyzer',
    'QualitativeAnalyzer',
    'AuditLogger',
    'VisualizationGenerator',
    'ReportGenerator'
]