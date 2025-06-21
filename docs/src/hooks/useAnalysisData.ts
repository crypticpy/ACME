/**
 * React hooks for accessing analysis data
 */

import { useEffect, useState } from 'react';
import { AnalysisData, ShareOfVoiceCategory, Theme, ProgramAnalysis } from '@/types/analysis';
import { getAnalysisData } from '@/lib/analysisData';

interface UseAnalysisDataReturn {
  data: AnalysisData | null;
  loading: boolean;
  error: Error | null;
}

export function useAnalysisData(): UseAnalysisDataReturn {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      try {
        setLoading(true);
        const analysisData = await getAnalysisData();
        if (!cancelled) {
          setData(analysisData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}

export function useShareOfVoice() {
  const { data, loading, error } = useAnalysisData();
  
  return {
    categories: data?.shareOfVoice.categories || [],
    loading,
    error
  };
}

export function useThemes(limit?: number) {
  const { data, loading, error } = useAnalysisData();
  
  const themes = data?.themes || [];
  const limitedThemes = limit ? themes.slice(0, limit) : themes;
  
  return {
    themes: limitedThemes,
    totalThemes: themes.length,
    loading,
    error
  };
}

export function useProgramAnalysis(programName?: string) {
  const { data, loading, error } = useAnalysisData();
  
  if (programName) {
    const program = data?.programs.find(p => p.name === programName);
    return {
      program: program || null,
      loading,
      error
    };
  }
  
  return {
    programs: data?.programs || [],
    loading,
    error
  };
}

export function useGeographicData(limit?: number) {
  const { data, loading, error } = useAnalysisData();
  
  const zipCodes = data?.geographic.zipCodes || [];
  const limitedZipCodes = limit ? zipCodes.slice(0, limit) : zipCodes;
  
  return {
    zipCodes: limitedZipCodes,
    totalZipCodes: zipCodes.length,
    loading,
    error
  };
}

export function useSummaryMetrics() {
  const { data, loading, error } = useAnalysisData();
  
  return {
    summary: data?.summary || null,
    loading,
    error
  };
}