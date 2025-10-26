"""
Supply Chain Planning - Scoring Module
Motor probabilístico de scoring CTE (Costo + Tiempo + Riesgo)
"""

from .base_scorer import (
    BaseScorer,
    CostBreakdown,
    TimeRiskAssessment,
    QualityRiskAssessment,
    CTEScore,
    NormalizedScore,
    ScoringContext,
    ScoringDimension,
)

from .criticality_scorer import (
    CriticalityAwareScorer,
    CriticalityLevel,
    ScoringRuleSet,
    DEFAULT_RULES,
    ScoringCutResult,
)

from .feature_extractor import (
    FeatureExtractor,
    FeatureVector,
    Feature,
    FeatureCategory,
    FeatureStatistics,
)

__all__ = [
    # Base Scorer
    "BaseScorer",
    "CostBreakdown",
    "TimeRiskAssessment",
    "QualityRiskAssessment",
    "CTEScore",
    "NormalizedScore",
    "ScoringContext",
    "ScoringDimension",
    
    # Criticality Scorer
    "CriticalityAwareScorer",
    "CriticalityLevel",
    "ScoringRuleSet",
    "DEFAULT_RULES",
    "ScoringCutResult",
    
    # Feature Extractor
    "FeatureExtractor",
    "FeatureVector",
    "Feature",
    "FeatureCategory",
    "FeatureStatistics",
]
