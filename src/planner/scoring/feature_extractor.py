"""
Feature scorer: genera features para machine learning y análisis
Extrae características técnicas, económicas y de riesgo
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics as stats_module
from enum import Enum
from .base_scorer import NormalizedScore, ScoringDimension


class FeatureCategory(str, Enum):
    """Categorías de features"""
    ECONOMIC = "ECONOMIC"
    TEMPORAL = "TEMPORAL"
    RELIABILITY = "RELIABILITY"
    OPERATIONAL = "OPERATIONAL"
    CONTEXTUAL = "CONTEXTUAL"


@dataclass
class Feature:
    """Una característica individual para modelo"""
    name: str
    category: FeatureCategory
    value: float
    unit: str = ""
    description: str = ""
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeatureVector:
    """Vector de features para una opción"""
    option_id: str
    item_id: str
    features: List[Feature] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_feature_by_name(self, name: str) -> Optional[Feature]:
        """Obtener feature por nombre"""
        for f in self.features:
            if f.name == name:
                return f
        return None
    
    def get_by_category(self, category: FeatureCategory) -> List[Feature]:
        """Obtener features de una categoría"""
        return [f for f in self.features if f.category == category]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'option_id': self.option_id,
            'item_id': self.item_id,
            'features': [f.to_dict() for f in self.features],
            'generated_at': self.generated_at.isoformat(),
        }
    
    def to_ml_vector(self) -> Tuple[List[str], List[float]]:
        """
        Convertir a vector para ML
        
        Returns:
            (nombres_features, valores_features)
        """
        names = [f.name for f in sorted(self.features, key=lambda x: x.name)]
        values = [f.value for f in sorted(self.features, key=lambda x: x.name)]
        return names, values


@dataclass
class FeatureStatistics:
    """Estadísticas de features en población"""
    feature_name: str
    mean: float
    median: float
    std_dev: float
    min_val: float
    max_val: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    
    @property
    def range(self) -> float:
        return self.max_val - self.min_val
    
    @property
    def coefficient_variation(self) -> float:
        """CV = std / mean"""
        return self.std_dev / max(self.mean, 0.01)
    
    @property
    def is_bimodal(self) -> bool:
        """Heurística: si CV > 0.5 y tiene outliers"""
        return self.coefficient_variation > 0.5


class FeatureExtractor:
    """Extrae features de opciones de abastecimiento"""
    
    def __init__(self):
        self.feature_vectors: List[FeatureVector] = []
        self.feature_stats: Dict[str, FeatureStatistics] = {}
    
    def extract_features(
        self,
        option_id: str,
        item_id: str,
        cost_data: Dict[str, float],
        time_data: Dict[str, float],
        reliability_data: Dict[str, float],
        context_data: Optional[Dict[str, Any]] = None,
    ) -> FeatureVector:
        """
        Extraer vector de features de una opción
        
        Args:
            option_id: ID de opción
            item_id: ID de ítem
            cost_data: {unit, transportation, customs, handling}
            time_data: {mean, std, p95, on_time_pct}
            reliability_data: {quality, availability, reliability}
            context_data: Datos contextuales
        
        Returns:
            FeatureVector con todas las características
        """
        features = []
        
        # === ECONOMIC FEATURES ===
        total_cost = (
            cost_data.get('unit', 0) +
            cost_data.get('transportation', 0) +
            cost_data.get('customs', 0) +
            cost_data.get('handling', 0)
        )
        
        features.append(Feature(
            name="total_cost_per_unit",
            category=FeatureCategory.ECONOMIC,
            value=total_cost,
            unit="USD",
            description="Costo total por unidad",
        ))
        
        features.append(Feature(
            name="logistics_cost_ratio",
            category=FeatureCategory.ECONOMIC,
            value=(cost_data.get('transportation', 0) + cost_data.get('customs', 0)) / max(total_cost, 0.01),
            unit="ratio",
            description="Costo logístico / Total",
        ))
        
        # === TEMPORAL FEATURES ===
        lt_mean = time_data.get('mean', 0)
        lt_std = time_data.get('std', 0)
        
        features.append(Feature(
            name="lead_time_mean",
            category=FeatureCategory.TEMPORAL,
            value=lt_mean,
            unit="days",
            description="Lead time promedio",
        ))
        
        features.append(Feature(
            name="lead_time_variability",
            category=FeatureCategory.TEMPORAL,
            value=lt_std / max(lt_mean, 1.0),
            unit="ratio",
            description="Variabilidad: std / mean",
        ))
        
        features.append(Feature(
            name="on_time_percentage",
            category=FeatureCategory.TEMPORAL,
            value=time_data.get('on_time_pct', 0.95),
            unit="ratio",
            description="Porcentaje histórico on-time",
        ))
        
        # === RELIABILITY FEATURES ===
        features.append(Feature(
            name="quality_acceptance_rate",
            category=FeatureCategory.RELIABILITY,
            value=reliability_data.get('quality', 0.99),
            unit="ratio",
            description="Tasa de aceptación QC",
        ))
        
        features.append(Feature(
            name="availability_percentage",
            category=FeatureCategory.RELIABILITY,
            value=reliability_data.get('availability', 0.95),
            unit="ratio",
            description="Disponibilidad del proveedor",
        ))
        
        integrated_reliability = (
            reliability_data.get('quality', 0.99) *
            reliability_data.get('availability', 0.95) *
            (reliability_data.get('reliability', 0.95) if reliability_data.get('reliability') else 1.0)
        )
        
        features.append(Feature(
            name="integrated_reliability",
            category=FeatureCategory.RELIABILITY,
            value=integrated_reliability,
            unit="ratio",
            description="Quality × Availability × Reliability",
        ))
        
        # === OPERATIONAL FEATURES ===
        if context_data:
            urgency_days = context_data.get('days_to_deadline', 999)
            
            features.append(Feature(
                name="urgency_flag",
                category=FeatureCategory.OPERATIONAL,
                value=1.0 if urgency_days <= 5 else 0.0,
                unit="binary",
                description="¿Es urgente? (<=5 días)",
            ))
            
            features.append(Feature(
                name="criticality_score",
                category=FeatureCategory.OPERATIONAL,
                value={'CRITICAL': 1.0, 'HIGH': 0.75, 'MEDIUM': 0.5, 'LOW': 0.25}.get(
                    context_data.get('criticality', 'MEDIUM'), 0.5
                ),
                unit="ratio",
                description="Criticidad del ítem",
            ))
            
            features.append(Feature(
                name="demand_volume",
                category=FeatureCategory.OPERATIONAL,
                value=context_data.get('demand_quantity', 1.0),
                unit="units",
                description="Cantidad demandada",
            ))
            
            # ABC classification impact
            abc = context_data.get('abc_class', 'B')
            features.append(Feature(
                name="abc_classification_value",
                category=FeatureCategory.OPERATIONAL,
                value={'A': 1.0, 'B': 0.5, 'C': 0.2}.get(abc, 0.5),
                unit="ratio",
                description="Valor ABC (A=1, B=0.5, C=0.2)",
            ))
        
        # === CONTEXTUAL FEATURES ===
        features.append(Feature(
            name="feature_vector_dimension",
            category=FeatureCategory.CONTEXTUAL,
            value=len(features),
            unit="count",
            description="Número de features extraídas",
        ))
        
        fv = FeatureVector(
            option_id=option_id,
            item_id=item_id,
            features=features,
        )
        
        self.feature_vectors.append(fv)
        return fv
    
    def calculate_statistics(self, feature_name: str) -> Optional[FeatureStatistics]:
        """
        Calcular estadísticas de un feature en población
        
        Args:
            feature_name: Nombre del feature
        
        Returns:
            FeatureStatistics o None si no existe feature
        """
        values = []
        
        for fv in self.feature_vectors:
            feat = fv.get_feature_by_name(feature_name)
            if feat:
                values.append(feat.value)
        
        if not values:
            return None
        
        values_sorted = sorted(values)
        
        stats_obj = FeatureStatistics(
            feature_name=feature_name,
            mean=stats_module.mean(values),
            median=stats_module.median(values),
            std_dev=stats_module.stdev(values) if len(values) > 1 else 0.0,
            min_val=min(values),
            max_val=max(values),
            percentile_25=values_sorted[len(values_sorted) // 4],
            percentile_75=values_sorted[3 * len(values_sorted) // 4],
            percentile_95=values_sorted[int(0.95 * len(values_sorted))] if len(values_sorted) > 1 else values_sorted[0],
        )
        
        self.feature_stats[feature_name] = stats_obj
        return stats_obj
    
    def normalize_feature(self, feature: Feature, stats: Optional[FeatureStatistics] = None) -> float:
        """
        Normalizar un feature a escala 0-1
        
        Args:
            feature: Feature a normalizar
            stats: Estadísticas de población (si no se proporciona, usa min/max del feature)
        
        Returns:
            Valor normalizado 0-1
        """
        if stats:
            if stats.range == 0:
                return 0.5
            return (feature.value - stats.min_val) / stats.range
        
        # Sin estadísticas, usar heurística
        if feature.category == FeatureCategory.TEMPORAL:
            # Normalizar LT a 0-1 (días)
            return min(1.0, max(0.0, feature.value / 100.0))
        elif feature.category == FeatureCategory.ECONOMIC:
            # Normalizar costo (típicamente 0-1000 USD)
            return min(1.0, max(0.0, feature.value / 1000.0))
        elif feature.category == FeatureCategory.RELIABILITY:
            # Ya en 0-1
            return feature.value
        
        return feature.value
    
    def generate_feature_report(self) -> str:
        """Generar reporte de features extraídas"""
        if not self.feature_vectors:
            return "No feature vectors extracted yet"
        
        lines = [
            f"Feature Extraction Report - {len(self.feature_vectors)} opciones",
            f"\nCategorías de features:",
        ]
        
        for category in FeatureCategory:
            count = sum(
                len(fv.get_by_category(category))
                for fv in self.feature_vectors
            )
            if count > 0:
                lines.append(f"  • {category.value}: {count // len(self.feature_vectors)} features/opción")
        
        lines.append(f"\nEjemplo de vector (opción 1):")
        if self.feature_vectors:
            fv = self.feature_vectors[0]
            for feat in fv.features[:5]:
                lines.append(f"  • {feat.name}: {feat.value:.4f} ({feat.unit})")
        
        return "\n".join(lines)
