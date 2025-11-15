"""
Contrato de interfaz para el módulo de planificación (Planner).

Este módulo define el port (interfaz) que debe implementar cualquier
servicio de planificación de abastecimiento, siguiendo arquitectura hexagonal.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class SourcingPath(str, Enum):
    """Vías de abastecimiento disponibles"""
    STOCK_LOCAL = "stock_local"              # Reserva de stock local
    RELEASE = "release"                      # Liberación de stock comprometido
    DISASSEMBLY = "disassembly"             # Desarme de activos
    SUBSTITUTE = "substitute"                # Sustitutos/equivalentes
    CTP = "ctp"                              # Capable to Promise
    TRANSFER = "transfer"                    # Transferencia entre almacenes
    EXPEDITE = "expedite"                    # Aceleración de pedidos
    PURCHASE = "purchase"                    # Compra a proveedor


class OptimizationStrategy(str, Enum):
    """Estrategias de optimización"""
    COST_MINIMIZATION = "cost_minimization"
    TIME_MINIMIZATION = "time_minimization"
    BALANCED = "balanced"
    CUSTOM = "custom"


class PlannerPort(ABC):
    """
    Port (interfaz) para servicios de planificación de abastecimiento.
    
    Este contrato define los métodos que debe implementar cualquier
    adaptador del módulo de planificación.
    """
    
    @abstractmethod
    def optimize_sourcing_options(
        self,
        item_id: str,
        required_quantity: float,
        required_date: datetime,
        criticality: str = "MEDIUM",
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimiza opciones de abastecimiento para un material.
        
        Args:
            item_id: Identificador del material
            required_quantity: Cantidad requerida
            required_date: Fecha requerida de entrega
            criticality: Nivel de criticidad (CRITICAL, HIGH, MEDIUM, LOW)
            strategy: Estrategia de optimización a aplicar
            constraints: Restricciones adicionales (presupuesto, lead time max, etc.)
            
        Returns:
            {
                "success": bool,
                "options": List[Dict],  # Opciones ordenadas por ranking
                "recommended_option": Dict,
                "total_cost": float,
                "total_lead_time": int,
                "confidence_score": float,
                "execution_time_ms": float,
                "metadata": Dict
            }
        """
        pass
    
    @abstractmethod
    def calculate_lead_times(
        self,
        item_id: str,
        supplier_id: Optional[str] = None,
        sourcing_path: Optional[SourcingPath] = None,
        service_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calcula lead times para un material según ruta de abastecimiento.
        
        Args:
            item_id: Identificador del material
            supplier_id: ID del proveedor (opcional)
            sourcing_path: Vía de abastecimiento específica
            service_level: Nivel de servicio para cálculo (0.95 = 95%)
            
        Returns:
            {
                "item_id": str,
                "mean_days": float,
                "std_dev_days": float,
                "p50_days": int,    # Mediana
                "p95_days": int,    # 95º percentil
                "p99_days": int,    # 99º percentil
                "confidence_level": float,
                "sample_size": int,
                "last_updated": datetime
            }
        """
        pass
    
    @abstractmethod
    def suggest_suppliers(
        self,
        item_id: str,
        required_quantity: float,
        max_suppliers: int = 5,
        ranking_criteria: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Sugiere proveedores para un material basado en múltiples criterios.
        
        Args:
            item_id: Identificador del material
            required_quantity: Cantidad requerida
            max_suppliers: Número máximo de proveedores a retornar
            ranking_criteria: Criterios de ranking (cost, lead_time, quality, etc.)
            
        Returns:
            [
                {
                    "supplier_id": str,
                    "supplier_name": str,
                    "unit_cost": float,
                    "lead_time_days": int,
                    "on_time_percentage": float,
                    "quality_acceptance_rate": float,
                    "ranking_score": float,
                    "competitive_rank": int
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def check_inventory_availability(
        self,
        item_id: str,
        required_quantity: float,
        warehouse_id: Optional[str] = None,
        include_reserved: bool = False,
        check_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Verifica disponibilidad de inventario para un material.
        
        Args:
            item_id: Identificador del material
            required_quantity: Cantidad requerida
            warehouse_id: Almacén específico (None = todos)
            include_reserved: Incluir stock reservado
            check_quality: Verificar solo stock aprobado
            
        Returns:
            {
                "available": bool,
                "quantity_on_hand": float,
                "quantity_available": float,
                "quantity_reserved": float,
                "quantity_allocated": float,
                "warehouse_distribution": List[Dict],
                "lots": List[Dict],
                "expiration_alerts": List[Dict]
            }
        """
        pass
    
    @abstractmethod
    def evaluate_substitutes(
        self,
        item_id: str,
        required_quantity: float,
        max_substitutes: int = 3,
        min_technical_match: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Evalúa materiales sustitutos para un ítem.
        
        Args:
            item_id: Identificador del material original
            required_quantity: Cantidad requerida
            max_substitutes: Número máximo de sustitutos a retornar
            min_technical_match: % mínimo de coincidencia técnica (0-1)
            
        Returns:
            [
                {
                    "substitute_id": str,
                    "substitute_code": str,
                    "technical_match": float,
                    "conversion_factor": float,
                    "cost_differential": float,
                    "availability": Dict,
                    "recommendation_score": float
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def run_algorithm(
        self,
        algorithm_type: str,
        input_data: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un algoritmo específico de optimización.
        
        Args:
            algorithm_type: Tipo de algoritmo (reserve_dynamic, release_marginal, etc.)
            input_data: Datos de entrada para el algoritmo
            parameters: Parámetros de configuración del algoritmo
            
        Returns:
            {
                "algorithm_type": str,
                "success": bool,
                "status": str,
                "result": Dict,
                "execution_time_ms": float,
                "metadata": Dict
            }
        """
        pass
    
    @abstractmethod
    def calculate_total_cost(
        self,
        sourcing_options: List[Dict[str, Any]],
        include_transportation: bool = True,
        include_customs: bool = True,
        include_handling: bool = True
    ) -> Dict[str, float]:
        """
        Calcula costo total de opciones de abastecimiento.
        
        Args:
            sourcing_options: Lista de opciones de abastecimiento
            include_transportation: Incluir costos de transporte
            include_customs: Incluir aranceles y aduanas
            include_handling: Incluir costos de manejo
            
        Returns:
            {
                "unit_cost": float,
                "transportation_cost": float,
                "customs_cost": float,
                "handling_cost": float,
                "total_cost_per_unit": float,
                "total_cost": float
            }
        """
        pass
    
    @abstractmethod
    def validate_capacity_constraints(
        self,
        resource_id: str,
        required_capacity: float,
        capacity_type: str,
        time_window_start: datetime,
        time_window_end: datetime
    ) -> Dict[str, Any]:
        """
        Valida restricciones de capacidad de un recurso.
        
        Args:
            resource_id: ID del recurso (proveedor, almacén, transporte)
            required_capacity: Capacidad requerida
            capacity_type: Tipo de capacidad (SUPPLIER_CAPACITY, WAREHOUSE_CAPACITY, etc.)
            time_window_start: Inicio de ventana temporal
            time_window_end: Fin de ventana temporal
            
        Returns:
            {
                "constraint_satisfied": bool,
                "available_capacity": float,
                "reserved_capacity": float,
                "utilization_percentage": float,
                "earliest_available_date": datetime,
                "recommendation": str
            }
        """
        pass
