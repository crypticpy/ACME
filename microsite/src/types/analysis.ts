/**
 * Type definitions for ACME Cultural Funding Analysis data
 */

export interface AnalysisSummary {
  totalResponses: number;
  responseRate: number;
  lastUpdated: string;
  geographicCoverage: number;
  themesIdentified: number;
  programsAnalyzed: number;
}

export interface ShareOfVoiceCategory {
  name: string;
  value: number;
  percentage: number;
  confidence: number;
}

export interface Theme {
  id: string;
  name: string;
  count: number;
  percentage: number;
  description: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'mixed';
  urgency: 'high' | 'medium' | 'low';
  keywords: string[];
  evidence?: string[];
}

export interface ProgramTheme {
  theme: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  frequency: number;
}

export interface ProgramAnalysis {
  name: string;
  responseCount: number;
  themes: ProgramTheme[];
}

export interface GeographicData {
  zipCode: string;
  count: number;
  percentage: number;
}

export interface AnalysisData {
  summary: AnalysisSummary;
  shareOfVoice: {
    categories: ShareOfVoiceCategory[];
  };
  themes: Theme[];
  programs: ProgramAnalysis[];
  geographic: {
    zipCodes: GeographicData[];
  };
}

export interface VisualizationFile {
  type: 'static' | 'interactive';
  category: string;
  fileName: string;
  path: string;
}