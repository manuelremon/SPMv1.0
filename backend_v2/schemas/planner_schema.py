"""
Backend v2.0 - Planner Schemas
Pydantic schemas para validación de requests/responses del módulo planner
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request para analizar opciones de aprovisionamiento"""
    item_id: str = Field(..., min_length=1, max_length=50, description="ID del item a aprovisionar")
    demand_quantity: float = Field(..., gt=0, description="Cantidad demandada")
    required_date: datetime = Field(..., description="Fecha requerida del material")
    criticality: str = Field(default="MEDIUM", description="Nivel de criticidad")
    budget_limit: Optional[float] = Field(None, ge=0, description="Límite presupuestario opcional")
    
    @field_validator("criticality")
    @classmethod
    def validate_criticality(cls, v: str) -> str:
        allowed = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        if v.upper() not in allowed:
            raise ValueError(f"Criticality must be one of {allowed}")
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "ITEM-001",
                "demand_quantity": 100.0,
                "required_date": "2025-12-01T00:00:00",
                "criticality": "HIGH",
                "budget_limit": 5000.0
            }
        }


class AlgorithmRecommendation(BaseModel):
    """Recomendación de un algoritmo individual"""
    algorithm: str = Field(..., description="Nombre del algoritmo")
    proposed_quantity: float = Field(..., description="Cantidad propuesta")
    estimated_cost: float = Field(..., description="Costo estimado")
    confidence_score: float = Field(..., ge=0, le=1, description="Score de confianza (0-1)")
    reasoning: str = Field(..., description="Explicación de la recomendación")
    selected_option: str = Field(..., description="Opción seleccionada por el algoritmo")
    status: str = Field(..., description="Estado de ejecución")


class CostRange(BaseModel):
    """Rango de costos entre todas las recomendaciones"""
    min: float = Field(..., ge=0, description="Costo mínimo")
    max: float = Field(..., ge=0, description="Costo máximo")
    avg: float = Field(..., ge=0, description="Costo promedio")


class AnalyzeResponse(BaseModel):
    """Response del análisis de aprovisionamiento"""
    ok: bool = Field(default=True)
    item_id: str
    demand_quantity: float
    required_date: str
    criticality: str
    recommendations: List[AlgorithmRecommendation]
    best_option: Optional[AlgorithmRecommendation]
    total_cost_range: CostRange
    algorithms_executed: int
    execution_time_seconds: float
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "ok": True,
                "item_id": "ITEM-001",
                "demand_quantity": 100.0,
                "required_date": "2025-12-01T00:00:00",
                "criticality": "HIGH",
                "recommendations": [
                    {
                        "algorithm": "RESERVE_DYNAMIC",
                        "proposed_quantity": 100.0,
                        "estimated_cost": 4500.0,
                        "confidence_score": 0.85,
                        "reasoning": "Liberar desde almacén WH-001...",
                        "selected_option": "reserve_from_wh_001",
                        "status": "COMPLETED"
                    }
                ],
                "best_option": {
                    "algorithm": "RESERVE_DYNAMIC",
                    "proposed_quantity": 100.0,
                    "estimated_cost": 4500.0,
                    "confidence_score": 0.85,
                    "reasoning": "Liberar desde almacén WH-001...",
                    "selected_option": "reserve_from_wh_001",
                    "status": "COMPLETED"
                },
                "total_cost_range": {
                    "min": 4200.0,
                    "max": 5800.0,
                    "avg": 4850.0
                },
                "algorithms_executed": 8,
                "execution_time_seconds": 0.145,
                "timestamp": "2025-11-13T10:30:00"
            }
        }


class ExecutePlanRequest(BaseModel):
    """Request para ejecutar un plan de aprovisionamiento"""
    item_id: str = Field(..., min_length=1)
    algorithm: str = Field(..., description="Algoritmo seleccionado")
    quantity: float = Field(..., gt=0)
    approved_by: Optional[str] = Field(None, description="Usuario que aprueba")
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        allowed = [
            "RESERVE_DYNAMIC",
            "PURCHASE_MULTICRITERION",
            "RELEASE_MARGINAL_COST",
            "TRANSFER_TDABC",
            "CTP_JOHNSON",
            "DISASSEMBLY_KNAPSACK",
            "EXPEDITE_PROBABILITY",
            "SUBSTITUTES_GRAPH"
        ]
        if v.upper() not in allowed:
            raise ValueError(f"Algorithm must be one of {allowed}")
        return v.upper()


class ExecutePlanResponse(BaseModel):
    """Response de ejecución de plan"""
    ok: bool = Field(default=True)
    plan_id: str = Field(..., description="ID del plan ejecutado")
    status: str = Field(..., description="Estado de ejecución")
    message: str
    timestamp: str


class PlanStatusResponse(BaseModel):
    """Response del estado de un plan"""
    ok: bool = Field(default=True)
    plan_id: str
    status: str
    item_id: str
    quantity: float
    algorithm_used: str
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response de error estandarizado"""
    ok: bool = Field(default=False)
    error: Dict[str, Any]
