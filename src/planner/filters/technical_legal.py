"""
Filtro Técnico-Legal (Nivel 1)
Descarta opciones de abastecimiento que no cumplen:
- Especificación técnica
- Normas de cumplimiento
- Restricciones legales/configuración
- Shelf-life
- Requisitos de trazabilidad
- Control de cambios
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from ..models.sourcing import SourcingOption, SourcingPath
from ..models.items import ItemMaster
from ..models.inventory import InventoryLot, QCStatus


class FilterReason(str, Enum):
    """Motivo por el cual se rechaza una opción"""
    SPEC_MISMATCH = "SPEC_MISMATCH"                    # Especificación no coincide
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"      # Viola norma requerida
    LICENSE_ISSUE = "LICENSE_ISSUE"                    # Problema de licencia/configuración
    SHELF_LIFE_INSUFFICIENT = "SHELF_LIFE_INSUFFICIENT"  # Vencimiento muy próximo
    TRACEABILITY_REQUIRED = "TRACEABILITY_REQUIRED"    # Requiere trazabilidad, opción no la tiene
    QUALITY_HOLD = "QUALITY_HOLD"                      # Lote en cuarentena/QC
    EXPIRED = "EXPIRED"                                # Lote expirado
    REGULATORY_HOLD = "REGULATORY_HOLD"                # Restricción regulatoria
    SUPPLIER_SUSPENDED = "SUPPLIER_SUSPENDED"          # Proveedor suspendido
    ENVIRONMENTAL_RESTRICTION = "ENVIRONMENTAL_RESTRICTION"  # Restricción ambiental
    LEAD_TIME_VIOLATION = "LEAD_TIME_VIOLATION"        # No cumple ventana requerida
    OBSOLETE = "OBSOLETE"                              # Ítem obsoleto
    CUSTOM_RULE = "CUSTOM_RULE"                        # Regla personalizada


@dataclass
class FilterResult:
    """Resultado del filtrado de una opción"""
    option_id: str
    feasible: bool
    reasons: List[FilterReason] = None
    rejection_notes: str = ""
    confidence_level: float = 1.0
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []


class TechnicalLegalFilter:
    """Filtro técnico-legal para opciones de abastecimiento"""
    
    def __init__(self):
        self.filter_rules: Dict[str, Any] = {}
        self.supplier_blacklist: set = set()
        self.suspended_suppliers: set = set()
        self.environmental_restrictions: Dict[str, List[str]] = {}  # item_id -> restricted_paths
        self.regulatory_requirements: Dict[str, List[str]] = {}  # item_id -> required_standards
        
    def register_supplier_as_suspended(self, supplier_id: str) -> None:
        """Suspender proveedor"""
        self.suspended_suppliers.add(supplier_id)
    
    def register_supplier_blacklist(self, supplier_id: str) -> None:
        """Agregar proveedor a lista negra"""
        self.supplier_blacklist.add(supplier_id)
    
    def set_environmental_restriction(self, item_id: str, sourcing_paths: List[str]) -> None:
        """Establecer restricción ambiental (ej: PURCHASE_IMPORT no permitido)"""
        self.environmental_restrictions[item_id] = sourcing_paths
    
    def set_regulatory_requirements(self, item_id: str, standards: List[str]) -> None:
        """Establecer normas requeridas (ISO, FDA, etc.)"""
        self.regulatory_requirements[item_id] = standards
    
    def filter_option(
        self,
        option: SourcingOption,
        item: ItemMaster,
        required_date: datetime = None,
        inventory_lot: Optional[InventoryLot] = None
    ) -> FilterResult:
        """
        Filtrar una opción de abastecimiento individual
        
        Args:
            option: Opción a evaluar
            item: Maestro del material
            required_date: Fecha requerida (para validar lead time)
            inventory_lot: Lote (si aplica, para opciones de stock)
        
        Returns:
            FilterResult con viabilidad y motivos de rechazo
        """
        result = FilterResult(option_id=option.option_id, feasible=True, reasons=[])
        
        # 1. SUPPLIER CHECKS
        if option.supplier_id:
            if option.supplier_id in self.supplier_blacklist:
                result.feasible = False
                result.reasons.append(FilterReason.LICENSE_ISSUE)
                result.rejection_notes = "Proveedor en lista negra"
                return result
            
            if option.supplier_id in self.suspended_suppliers:
                result.feasible = False
                result.reasons.append(FilterReason.SUPPLIER_SUSPENDED)
                result.rejection_notes = "Proveedor suspendido"
                return result
        
        # 2. INVENTORY LOT QUALITY CHECK (si aplica)
        if inventory_lot:
            if inventory_lot.is_expired:
                result.feasible = False
                result.reasons.append(FilterReason.EXPIRED)
                result.rejection_notes = f"Lote expirado: {inventory_lot.expiration_date}"
                return result
            
            if inventory_lot.qc_status == QCStatus.REJECTED:
                result.feasible = False
                result.reasons.append(FilterReason.QUALITY_HOLD)
                result.rejection_notes = "Lote rechazado por QC"
                return result
            
            if inventory_lot.qc_status == QCStatus.QUARANTINE:
                result.feasible = False
                result.reasons.append(FilterReason.QUALITY_HOLD)
                result.rejection_notes = "Lote en cuarentena"
                return result
            
            # Check critical expiration if shelf-life is required
            if item.shelf_life_days and inventory_lot.is_critical_expiration(threshold_days=7):
                result.feasible = False
                result.reasons.append(FilterReason.SHELF_LIFE_INSUFFICIENT)
                result.rejection_notes = f"Shelf-life insuficiente: {inventory_lot.days_to_expiration} días"
                return result
        
        # 3. SHELF-LIFE CHECK (si aplica)
        if item.shelf_life_days and required_date:
            # Validar que hay suficiente tiempo para consumo
            # (Aquí se asume que el material llega "hoy" en esta opción)
            # Se necesita: hoy + min(14 días almacenaje) < vencimiento
            min_days_storage = 14
            if item.shelf_life_days < min_days_storage:
                result.feasible = False
                result.reasons.append(FilterReason.SHELF_LIFE_INSUFFICIENT)
                result.rejection_notes = f"Shelf-life {item.shelf_life_days}d < almacenaje mín {min_days_storage}d"
                return result
        
        # 4. TRACEABILITY CHECK
        if item.requires_traceability:
            # La opción debe tener trazabilidad (supplier_id + lot number, etc.)
            if option.sourcing_path.value == "STOCK_LOCAL":
                # Stock local es aceptable si el lote tiene datos
                if inventory_lot and not inventory_lot.lot_number:
                    result.feasible = False
                    result.reasons.append(FilterReason.TRACEABILITY_REQUIRED)
                    result.rejection_notes = "Requiere trazabilidad pero lote sin número"
                    return result
            elif option.sourcing_path.value in ["EQUIVALENT", "DISASSEMBLY", "RECOVERY"]:
                # Estas rutas pueden tener problemas de trazabilidad
                result.feasible = False
                result.reasons.append(FilterReason.TRACEABILITY_REQUIRED)
                result.rejection_notes = f"Ruta {option.sourcing_path} no garantiza trazabilidad"
                return result
        
        # 5. COMPLIANCE STANDARDS CHECK
        if item_id := item.item_id:
            if item_id in self.regulatory_requirements:
                required_standards = self.regulatory_requirements[item_id]
                item_standards = set(item.compliance_standards or [])
                
                if not all(std in item_standards for std in required_standards):
                    missing = set(required_standards) - item_standards
                    result.feasible = False
                    result.reasons.append(FilterReason.COMPLIANCE_VIOLATION)
                    result.rejection_notes = f"Normas faltantes: {', '.join(missing)}"
                    return result
        
        # 6. ENVIRONMENTAL RESTRICTIONS CHECK
        if item.item_id in self.environmental_restrictions:
            restricted_paths = self.environmental_restrictions[item.item_id]
            if option.sourcing_path.value in restricted_paths:
                result.feasible = False
                result.reasons.append(FilterReason.ENVIRONMENTAL_RESTRICTION)
                result.rejection_notes = f"Ruta {option.sourcing_path} prohibida por regulación ambiental"
                return result
        
        # 7. LEAD TIME FEASIBILITY CHECK
        if required_date and option.lead_time_days_mean is not None:
            # Calcular fecha de entrega más probable
            delivery_date = datetime.utcnow() + timedelta(days=option.lead_time_days_mean)
            if delivery_date > required_date:
                result.feasible = False
                result.reasons.append(FilterReason.LEAD_TIME_VIOLATION)
                result.rejection_notes = f"Lead time {option.lead_time_days_mean}d excede requerido"
                return result
        
        # 8. SPECIFICATIONS MATCH CHECK (simplificado)
        if item.specifications and len(item.specifications) > 0:
            # Para opciones equivalentes, verificar que hay equivalentes registrados
            if option.sourcing_path.value == "EQUIVALENT":
                # Si no hay equivalentes definidos en el maestro, rechazamos
                if not item.equivalent_items or len(item.equivalent_items) == 0:
                    result.feasible = False
                    result.reasons.append(FilterReason.SPEC_MISMATCH)
                    result.rejection_notes = "No hay ítems equivalentes definidos"
                    return result
                
                # Verificar que el equivalente está en la lista con buen match
                equiv_found = False
                for equiv in item.equivalent_items:
                    if equiv.equivalent_id in option.option_id:  # Rough check
                        if equiv.technical_specs_match >= 0.85:
                            equiv_found = True
                            break
                
                if not equiv_found:
                    result.feasible = False
                    result.reasons.append(FilterReason.SPEC_MISMATCH)
                    result.rejection_notes = "Equivalente sin suficiente match técnico (< 85%)"
                    return result
        
        # 9. ITEM OBSOLESCENCE CHECK
        if item.active == False:
            result.feasible = False
            result.reasons.append(FilterReason.OBSOLETE)
            result.rejection_notes = "Ítem marcado como inactivo/obsoleto"
            return result
        
        # If all checks pass
        result.feasible = True
        result.reasons = []
        return result
    
    def filter_path(
        self,
        path: SourcingPath,
        item: ItemMaster,
        inventory_lots: Optional[Dict[str, InventoryLot]] = None
    ) -> SourcingPath:
        """
        Filtrar todas las opciones en una ruta de abastecimiento
        
        Args:
            path: Ruta con múltiples opciones
            item: Maestro del material
            inventory_lots: Diccionario {lot_number -> InventoryLot} para stock local
        
        Returns:
            path actualizado con opciones filtradas
        """
        inventory_lots = inventory_lots or {}
        
        # Filtrar cada opción
        for option in path.options:
            # Buscar lote si es stock local
            inventory_lot = None
            if option.sourcing_path.value == "STOCK_LOCAL" and option.option_id in inventory_lots:
                inventory_lot = inventory_lots[option.option_id]
            
            # Aplicar filtro
            filter_result = self.filter_option(
                option=option,
                item=item,
                required_date=path.required_date,
                inventory_lot=inventory_lot
            )
            
            # Actualizar opción
            option.feasible = filter_result.feasible
            option.feasibility_notes = filter_result.rejection_notes
        
        # Recalcular totales
        path.calculate_total_feasible()
        
        return path
    
    def get_feasible_options(self, path: SourcingPath) -> List[SourcingOption]:
        """Retornar solo opciones viables"""
        return [opt for opt in path.options if opt.feasible]
    
    def generate_filter_report(self, path: SourcingPath) -> Dict[str, Any]:
        """
        Generar reporte del filtrado
        
        Returns:
            Reporte con estadísticas y detalles
        """
        total_options = len(path.options)
        feasible = self.get_feasible_options(path)
        infeasible = [opt for opt in path.options if not opt.feasible]
        
        report = {
            "path_id": path.path_id,
            "total_options": total_options,
            "feasible_count": len(feasible),
            "infeasible_count": len(infeasible),
            "feasibility_rate": len(feasible) / max(1, total_options),
            "has_solution": path.has_feasible_solution,
            "feasible_options": [
                {
                    "option_id": opt.option_id,
                    "sourcing_path": opt.sourcing_path,
                    "quantity_available": opt.quantity_available,
                    "total_cost_per_unit": opt.total_cost_per_unit
                }
                for opt in feasible
            ],
            "rejected_options": [
                {
                    "option_id": opt.option_id,
                    "sourcing_path": opt.sourcing_path,
                    "reason": opt.feasibility_notes
                }
                for opt in infeasible
            ]
        }
        
        return report
