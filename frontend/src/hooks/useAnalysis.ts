import { useState, useEffect, useCallback } from 'react';
import { Analysis } from '../types/analysis';
import { Forecast } from '../types/forecast';
import { ImpactGraphData } from '../types/impact';
import { EvidenceReport } from '../types/evidence';
import { Recommendation, DeploymentDecision } from '../types/recommendation';
import { DeploymentOutcome } from '../types/outcome';
import { getAnalysisById } from '../api/analyses';
import { getForecastByAnalysisId } from '../api/forecasts';
import { getImpactGraphByAnalysisId } from '../api/impact';
import { getEvidenceByAnalysisId } from '../api/evidence';
import { getRecommendationsByAnalysisId, getDeploymentDecision, submitDeploymentDecision } from '../api/recommendations';
import { getOutcomeByAnalysisId } from '../api/outcomes';

export interface UseAnalysisReturn {
  analysis: Analysis | null;
  forecast: Forecast | null;
  impactGraph: ImpactGraphData | null;
  evidence: EvidenceReport | null;
  recommendations: Recommendation[];
  decision: DeploymentDecision | null;
  outcome: DeploymentOutcome | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  makeDecision: (decisionType: 'approved_controlled_test' | 'review_requested', note?: string) => Promise<void>;
}

export function useAnalysis(analysisId: string = 'analysis-pr-248'): UseAnalysisReturn {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [impactGraph, setImpactGraph] = useState<ImpactGraphData | null>(null);
  const [evidence, setEvidence] = useState<EvidenceReport | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [decision, setDecision] = useState<DeploymentDecision | null>(null);
  const [outcome, setOutcome] = useState<DeploymentOutcome | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        analysisData,
        forecastData,
        impactData,
        evidenceData,
        recData,
        decisionData,
        outcomeData,
      ] = await Promise.all([
        getAnalysisById(analysisId),
        getForecastByAnalysisId(analysisId),
        getImpactGraphByAnalysisId(analysisId),
        getEvidenceByAnalysisId(analysisId),
        getRecommendationsByAnalysisId(analysisId),
        getDeploymentDecision(analysisId),
        getOutcomeByAnalysisId(analysisId),
      ]);

      setAnalysis(analysisData);
      setForecast(forecastData);
      setImpactGraph(impactData);
      setEvidence(evidenceData);
      setRecommendations(recData);
      setDecision(decisionData);
      setOutcome(outcomeData);
    } catch (err: any) {
      setError(err?.message || 'Failed to load analysis telemetry data');
    } finally {
      setLoading(false);
    }
  }, [analysisId]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const makeDecision = async (
    decisionType: 'approved_controlled_test' | 'review_requested',
    note?: string
  ) => {
    try {
      const updated = await submitDeploymentDecision(analysisId, decisionType, note);
      setDecision(updated);
    } catch (err: any) {
      setError(err?.message || 'Failed to submit decision');
    }
  };

  return {
    analysis,
    forecast,
    impactGraph,
    evidence,
    recommendations,
    decision,
    outcome,
    loading,
    error,
    refresh: fetchAll,
    makeDecision,
  };
}
