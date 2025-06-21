"""Executive report generation module."""

from .generator import ReportGenerator
from .templates import ReportTemplate, ExecutiveSummaryTemplate

__all__ = ['ReportGenerator', 'ReportTemplate', 'ExecutiveSummaryTemplate']