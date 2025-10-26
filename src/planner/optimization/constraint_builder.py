"""
Construcción de restricciones para el modelo MIP/ILP de portafolio.

Restricciones soportadas:
1. Demanda mínima: Σ qty_option·x ≥ demand
2. FEFO (First-Expire-First-Out): orden de consumo por fecha de vencimiento
3. Capacidad de inventario: por ubicación, centro de distribución
4. Lead time: entrega dentro del deadline
5. Service Level: disponibilidad mínima requerida
6. Transferencias: entre centros (costo de transporte)
7. One-in: máximo un proveedor por opción
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Tipos de restricciones en el modelo."""
    DEMAND = "demand"                      # Σ qty·x ≥ demand
    FEFO = "fefo"                          # Orden de consumo
    CAPACITY = "capacity"                  # Inventario máximo
    LEAD_TIME = "lead_time"                # Entrega a tiempo
    SERVICE_LEVEL = "service_level"        # Disponibilidad mínima
    TRANSFER = "transfer"                  # Transferencias entre centros
    ONE_IN = "one_in"                      # Máximo un proveedor
    BUDGET = "budget"                      # Límite de presupuesto
    SOURCING = "sourcing"                  # Preferencia de fuentes


@dataclass
class DemandConstraint:
    """Restricción de demanda mínima."""
    item_id: str
    quantity_required: float
    unit_of_measure: str
    
    def __post_init__(self):
        if self.quantity_required <= 0:
            raise ValueError(f"Demanda debe ser > 0, recibido: {self.quantity_required}")


@dataclass
class FEFOConstraint:
    """Restricción FEFO: consumir por fecha de vencimiento."""
    item_id: str
    batches: List[Dict[str, any]]  # [{"batch_id": "...", "exp_date": "...", "qty": X}]
    consumption_sequence: List[str] = field(default_factory=list)  # Orden ordenada por exp_date
    
    def apply(self) -> List[str]:
        """Ordena lotes por fecha de vencimiento ascendente."""
        sorted_batches = sorted(
            self.batches,
            key=lambda b: b.get("exp_date", "9999-12-31")
        )
        self.consumption_sequence = [b["batch_id"] for b in sorted_batches]
        return self.consumption_sequence


@dataclass
class CapacityConstraint:
    """Restricción de capacidad de inventario."""
    location_id: str
    max_units: float
    max_value: Optional[float] = None  # Límite de valor en $ si aplica
    current_inventory: float = 0.0
    
    @property
    def available_capacity(self) -> float:
        """Capacidad disponible."""
        return max(0, self.max_units - self.current_inventory)
    
    @property
    def utilization_rate(self) -> float:
        """% de utilización."""
        if self.max_units == 0:
            return 0.0
        return (self.current_inventory / self.max_units) * 100


@dataclass
class LeadTimeConstraint:
    """Restricción de lead time."""
    option_id: str
    required_date: str              # Deadline (YYYY-MM-DD)
    lead_time_mean_days: float
    lead_time_std_days: float
    service_level_percentile: float = 0.95
    
    @property
    def sl_lead_time_days(self) -> float:
        """Lead time con SL objetivo (usando PPF de normal)."""
        from scipy.stats import norm
        z_score = norm.ppf(self.service_level_percentile)
        return self.lead_time_mean_days + z_score * self.lead_time_std_days


@dataclass
class ServiceLevelConstraint:
    """Restricción de disponibilidad mínima."""
    item_id: str
    min_service_level: float  # 0.95 = 95%
    current_availability: Optional[float] = None
    
    @property
    def is_compliant(self) -> bool:
        """¿Cumple el SL mínimo?"""
        if self.current_availability is None:
            return False
        return self.current_availability >= self.min_service_level


@dataclass
class TransferConstraint:
    """Restricción de transferencia entre centros."""
    from_location: str
    to_location: str
    max_transfer_qty: Optional[float] = None
    transfer_cost_per_unit: float = 0.0
    transfer_lead_time_days: int = 0
    
    @property
    def transfer_cost_total(self) -> float:
        """Costo total si se transfiere qty."""
        if self.max_transfer_qty is None:
            return 0.0
        return self.transfer_cost_per_unit * self.max_transfer_qty


@dataclass
class OneInConstraint:
    """Restricción: máximo un proveedor (supplier) por ítem."""
    item_id: str
    allowed_suppliers: List[str]  # Proveedores permitidos
    
    def __post_init__(self):
        if len(self.allowed_suppliers) == 0:
            raise ValueError(f"Al menos 1 proveedor requerido para {self.item_id}")


@dataclass
class BudgetConstraint:
    """Restricción de presupuesto total."""
    total_budget: float
    currency: str = "USD"
    contingency_pct: float = 0.0  # % de contingencia
    
    @property
    def available_budget(self) -> float:
        """Presupuesto disponible después de contingencia."""
        return self.total_budget * (1 - self.contingency_pct / 100)


@dataclass
class SourcingPreferenceConstraint:
    """Restricción de preferencia de fuentes (soft constraint)."""
    item_id: str
    preferred_supplier: str
    penalty_multiplier: float = 1.2  # Si no usa preferido, multiplica costo
    

class ConstraintBuilder:
    """Constructor de restricciones para MIP."""
    
    def __init__(self):
        """Inicializa el builder."""
        self.constraints: Dict[ConstraintType, List] = {
            ct: [] for ct in ConstraintType
        }
        self.logger = logger
    
    def add_demand_constraint(
        self,
        item_id: str,
        quantity_required: float,
        unit_of_measure: str
    ) -> "ConstraintBuilder":
        """Agrega restricción de demanda."""
        constraint = DemandConstraint(
            item_id=item_id,
            quantity_required=quantity_required,
            unit_of_measure=unit_of_measure
        )
        self.constraints[ConstraintType.DEMAND].append(constraint)
        self.logger.debug(f"Restricción demanda: {item_id} >= {quantity_required} {unit_of_measure}")
        return self
    
    def add_fefo_constraint(
        self,
        item_id: str,
        batches: List[Dict[str, any]]
    ) -> "ConstraintBuilder":
        """Agrega restricción FEFO."""
        constraint = FEFOConstraint(item_id=item_id, batches=batches)
        constraint.apply()
        self.constraints[ConstraintType.FEFO].append(constraint)
        self.logger.debug(f"Restricción FEFO: {item_id} con {len(batches)} lotes")
        return self
    
    def add_capacity_constraint(
        self,
        location_id: str,
        max_units: float,
        max_value: Optional[float] = None,
        current_inventory: float = 0.0
    ) -> "ConstraintBuilder":
        """Agrega restricción de capacidad."""
        constraint = CapacityConstraint(
            location_id=location_id,
            max_units=max_units,
            max_value=max_value,
            current_inventory=current_inventory
        )
        self.constraints[ConstraintType.CAPACITY].append(constraint)
        self.logger.debug(f"Restricción capacidad: {location_id} máx {max_units} unidades")
        return self
    
    def add_lead_time_constraint(
        self,
        option_id: str,
        required_date: str,
        lead_time_mean_days: float,
        lead_time_std_days: float,
        service_level_percentile: float = 0.95
    ) -> "ConstraintBuilder":
        """Agrega restricción de lead time."""
        constraint = LeadTimeConstraint(
            option_id=option_id,
            required_date=required_date,
            lead_time_mean_days=lead_time_mean_days,
            lead_time_std_days=lead_time_std_days,
            service_level_percentile=service_level_percentile
        )
        self.constraints[ConstraintType.LEAD_TIME].append(constraint)
        self.logger.debug(f"Restricción LT: {option_id} deadline {required_date}")
        return self
    
    def add_service_level_constraint(
        self,
        item_id: str,
        min_service_level: float,
        current_availability: Optional[float] = None
    ) -> "ConstraintBuilder":
        """Agrega restricción de SL."""
        constraint = ServiceLevelConstraint(
            item_id=item_id,
            min_service_level=min_service_level,
            current_availability=current_availability
        )
        self.constraints[ConstraintType.SERVICE_LEVEL].append(constraint)
        self.logger.debug(f"Restricción SL: {item_id} >= {min_service_level*100}%")
        return self
    
    def add_transfer_constraint(
        self,
        from_location: str,
        to_location: str,
        max_transfer_qty: Optional[float] = None,
        transfer_cost_per_unit: float = 0.0,
        transfer_lead_time_days: int = 0
    ) -> "ConstraintBuilder":
        """Agrega restricción de transferencia."""
        constraint = TransferConstraint(
            from_location=from_location,
            to_location=to_location,
            max_transfer_qty=max_transfer_qty,
            transfer_cost_per_unit=transfer_cost_per_unit,
            transfer_lead_time_days=transfer_lead_time_days
        )
        self.constraints[ConstraintType.TRANSFER].append(constraint)
        self.logger.debug(f"Restricción transferencia: {from_location} -> {to_location}")
        return self
    
    def add_one_in_constraint(
        self,
        item_id: str,
        allowed_suppliers: List[str]
    ) -> "ConstraintBuilder":
        """Agrega restricción de máximo 1 proveedor."""
        constraint = OneInConstraint(
            item_id=item_id,
            allowed_suppliers=allowed_suppliers
        )
        self.constraints[ConstraintType.ONE_IN].append(constraint)
        self.logger.debug(f"Restricción one-in: {item_id} con {len(allowed_suppliers)} opciones")
        return self
    
    def add_budget_constraint(
        self,
        total_budget: float,
        currency: str = "USD",
        contingency_pct: float = 0.0
    ) -> "ConstraintBuilder":
        """Agrega restricción de presupuesto."""
        constraint = BudgetConstraint(
            total_budget=total_budget,
            currency=currency,
            contingency_pct=contingency_pct
        )
        self.constraints[ConstraintType.BUDGET].append(constraint)
        self.logger.debug(f"Restricción presupuesto: {currency} {total_budget}")
        return self
    
    def add_sourcing_preference_constraint(
        self,
        item_id: str,
        preferred_supplier: str,
        penalty_multiplier: float = 1.2
    ) -> "ConstraintBuilder":
        """Agrega restricción de preferencia (soft)."""
        constraint = SourcingPreferenceConstraint(
            item_id=item_id,
            preferred_supplier=preferred_supplier,
            penalty_multiplier=penalty_multiplier
        )
        self.constraints[ConstraintType.SOURCING].append(constraint)
        self.logger.debug(f"Restricción preferencia: {item_id} preferido {preferred_supplier}")
        return self
    
    def get_constraints(self, constraint_type: Optional[ConstraintType] = None) -> Dict[ConstraintType, List]:
        """Retorna todas las restricciones o filtradas por tipo."""
        if constraint_type is None:
            return self.constraints
        return {constraint_type: self.constraints.get(constraint_type, [])}
    
    def get_constraint_summary(self) -> Dict[str, int]:
        """Retorna resumen de restricciones por tipo."""
        return {
            ct.value: len(constraints)
            for ct, constraints in self.constraints.items()
            if len(constraints) > 0
        }
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Valida consistencia de restricciones."""
        issues = []
        
        # Validar: si hay FEFO, debe haber inventario
        if self.constraints[ConstraintType.FEFO] and not self.constraints[ConstraintType.CAPACITY]:
            issues.append("FEFO requerido pero sin restricciones de capacidad")
        
        # Validar: presupuesto vs demanda
        if self.constraints[ConstraintType.BUDGET] and self.constraints[ConstraintType.DEMAND]:
            # Validación básica (sin datos numéricos aquí)
            pass
        
        return len(issues) == 0, issues
    
    def build(self) -> Dict[ConstraintType, List]:
        """Construye y retorna el modelo de restricciones."""
        is_valid, issues = self.validate()
        if not is_valid:
            self.logger.warning(f"Restricciones con issues: {issues}")
        return self.constraints
    
    def clear(self):
        """Limpia todas las restricciones."""
        for ct in ConstraintType:
            self.constraints[ct] = []
        self.logger.debug("Restricciones limpiadas")


# Aliases convenientes
class ConstraintSet:
    """Conjunto de restricciones construidas."""
    
    def __init__(self, constraints_dict: Dict[ConstraintType, List]):
        """Inicializa con dict de restricciones."""
        self.constraints = constraints_dict
    
    @property
    def demand_constraints(self) -> List[DemandConstraint]:
        return self.constraints.get(ConstraintType.DEMAND, [])
    
    @property
    def fefo_constraints(self) -> List[FEFOConstraint]:
        return self.constraints.get(ConstraintType.FEFO, [])
    
    @property
    def capacity_constraints(self) -> List[CapacityConstraint]:
        return self.constraints.get(ConstraintType.CAPACITY, [])
    
    @property
    def lead_time_constraints(self) -> List[LeadTimeConstraint]:
        return self.constraints.get(ConstraintType.LEAD_TIME, [])
    
    @property
    def service_level_constraints(self) -> List[ServiceLevelConstraint]:
        return self.constraints.get(ConstraintType.SERVICE_LEVEL, [])
    
    @property
    def transfer_constraints(self) -> List[TransferConstraint]:
        return self.constraints.get(ConstraintType.TRANSFER, [])
    
    @property
    def one_in_constraints(self) -> List[OneInConstraint]:
        return self.constraints.get(ConstraintType.ONE_IN, [])
    
    @property
    def budget_constraints(self) -> List[BudgetConstraint]:
        return self.constraints.get(ConstraintType.BUDGET, [])
    
    @property
    def sourcing_preference_constraints(self) -> List[SourcingPreferenceConstraint]:
        return self.constraints.get(ConstraintType.SOURCING, [])
