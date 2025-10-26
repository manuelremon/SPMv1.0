"""
Árbol de decisión con 12 vías operativas.

Flujo:
1. Stock local (liberación simple)
2. Stock local + assets (liberación con activos)
3. Desarme (desmontar BOM)
4. Sustitutos (equivalencias)
5. Recupero (reciclaje/desmontaje)
6. Transferencia (entre centros)
7. Intercompañía (compra a affiliated)
8. VMI (Vendor-Managed Inventory)
9. Préstamo (entre partners)
10. Acelerar (rush delivery)
11. Compra (proveedor standard)
12. Resultado final

Cada nodo tiene gates (puertas de decisión) que determinan si continuar.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SourceRoute(Enum):
    """Las 12 vías operativas."""
    STOCK_LOCAL = 1
    STOCK_LOCAL_ASSETS = 2
    DISASSEMBLY = 3
    SUBSTITUTES = 4
    RECOVERY = 5
    TRANSFER = 6
    INTERCOMPANY = 7
    VMI = 8
    LOAN = 9
    EXPEDITE = 10
    PURCHASE = 11
    FINAL_RESULT = 12


class GateType(Enum):
    """Tipos de gates (puertas de decisión)."""
    AVAILABILITY = "availability"         # ¿Disponible?
    TIMING = "timing"                     # ¿Tiempo suficiente?
    COST = "cost"                         # ¿Costo aceptable?
    QUALITY = "quality"                   # ¿Calidad OK?
    RISK = "risk"                         # ¿Riesgo bajo?
    REGULATORY = "regulatory"             # ¿Cumple normativa?
    RELATIONSHIP = "relationship"         # ¿Relación disponible?
    FORECAST = "forecast"                 # ¿Forecast OK?
    COMPLEX = "complex"                   # Decision lógica compleja


@dataclass
class Gate:
    """Puerta de decisión en un nodo."""
    gate_id: str
    gate_type: GateType
    description: str
    condition_func: Optional[Callable[[Union[Dict[str, Any], Any]], bool]] = None
    threshold: Optional[float] = None
    
    def evaluate(self, context: Union[Dict[str, Any], Any]) -> bool:
        """Evalúa si el gate se abre (True) o cierra (False)."""
        if self.condition_func:
            return self.condition_func(context)
        return True


@dataclass
class DecisionNode:
    """Nodo del árbol de decisión."""
    node_id: str
    route: SourceRoute
    name: str
    description: str
    
    # Gates que debe pasar
    gates: List[Gate] = field(default_factory=list)
    
    # Nodos siguientes (si gate abre/cierra)
    next_on_success: Optional["DecisionNode"] = None
    next_on_failure: Optional["DecisionNode"] = None
    
    # Metadata
    estimated_lead_time_days: float = 0.0
    estimated_cost: float = 0.0
    estimated_success_rate: float = 0.0  # 0-1
    
    def add_gate(self, gate: Gate) -> "DecisionNode":
        """Agrega un gate al nodo."""
        self.gates.append(gate)
        return self
    
    def set_success_path(self, next_node: "DecisionNode") -> "DecisionNode":
        """Establece nodo siguiente si gates abren."""
        self.next_on_success = next_node
        return self
    
    def set_failure_path(self, next_node: "DecisionNode") -> "DecisionNode":
        """Establece nodo siguiente si gates cierran."""
        self.next_on_failure = next_node
        return self
    
    def evaluate_gates(self, context: Union[Dict[str, Any], Any]) -> Tuple[bool, List[str]]:
        """
        Evalúa todos los gates del nodo.
        
        Returns:
            (all_pass, failed_gate_ids)
        """
        failed_gates = []
        
        for gate in self.gates:
            try:
                result = gate.evaluate(context)
                if not result:
                    failed_gates.append(gate.gate_id)
                    logger.debug(f"Gate CERRADO: {gate.gate_id} ({gate.description})")
                else:
                    logger.debug(f"Gate ABIERTO: {gate.gate_id}")
            except Exception as e:
                logger.error(f"Error evaluando gate {gate.gate_id}: {e}")
                failed_gates.append(gate.gate_id)
        
        all_pass = len(failed_gates) == 0
        return all_pass, failed_gates
    
    def get_path_info(self) -> Dict[str, Any]:
        """Información del camino en este nodo."""
        return {
            "node_id": self.node_id,
            "route": self.route.name,
            "route_number": self.route.value,
            "name": self.name,
            "description": self.description,
            "num_gates": len(self.gates),
            "gates": [{"id": g.gate_id, "type": g.gate_type.value, "desc": g.description} 
                     for g in self.gates],
            "estimated_lead_time": self.estimated_lead_time_days,
            "estimated_cost": self.estimated_cost,
            "estimated_success_rate": self.estimated_success_rate
        }


@dataclass
class ExecutionPath:
    """Camino de ejecución del árbol."""
    path_id: str
    item_id: str
    demand_quantity: float
    required_date: str
    
    # Nodos visitados
    visited_nodes: List[str] = field(default_factory=list)
    
    # Resultado de cada nodo
    node_results: Dict[str, Tuple[bool, List[str]]] = field(default_factory=dict)
    
    # Resultado final
    final_success: bool = False
    final_route: Optional[SourceRoute] = None
    total_lead_time: float = 0.0
    total_cost: float = 0.0
    selected_source: Optional[str] = None
    
    def add_node_visit(self, node_id: str, success: bool, failed_gates: List[str]):
        """Registra visita a un nodo."""
        self.visited_nodes.append(node_id)
        self.node_results[node_id] = (success, failed_gates)
    
    def set_result(self, success: bool, route: SourceRoute, source: str, 
                   lead_time: float, cost: float):
        """Establece resultado final."""
        self.final_success = success
        self.final_route = route
        self.selected_source = source
        self.total_lead_time = lead_time
        self.total_cost = cost
    
    def get_summary(self) -> Dict[str, Any]:
        """Resumen de la ejecución."""
        return {
            "path_id": self.path_id,
            "item_id": self.item_id,
            "demand": self.demand_quantity,
            "required_date": self.required_date,
            "success": self.final_success,
            "route": self.final_route.name if self.final_route else None,
            "route_number": self.final_route.value if self.final_route else None,
            "source": self.selected_source,
            "lead_time": self.total_lead_time,
            "cost": self.total_cost,
            "nodes_visited": self.visited_nodes,
            "num_nodes": len(self.visited_nodes),
            "num_gates_failed": sum(len(failed) for _, failed in self.node_results.values())
        }


class DecisionTreeBuilder:
    """Constructor del árbol de decisión."""
    
    def __init__(self):
        """Inicializa builder."""
        self.root_node: Optional[DecisionNode] = None
        self.all_nodes: Dict[str, DecisionNode] = {}
    
    def create_node(
        self,
        node_id: str,
        route: SourceRoute,
        name: str,
        description: str,
        lead_time: float = 0,
        cost: float = 0,
        success_rate: float = 0.8
    ) -> DecisionNode:
        """Crea un nodo en el árbol."""
        node = DecisionNode(
            node_id=node_id,
            route=route,
            name=name,
            description=description,
            estimated_lead_time_days=lead_time,
            estimated_cost=cost,
            estimated_success_rate=success_rate
        )
        self.all_nodes[node_id] = node
        
        if self.root_node is None:
            self.root_node = node
        
        return node
    
    def add_gate_to_node(
        self,
        node_id: str,
        gate_id: str,
        gate_type: GateType,
        description: str,
        condition_func: Optional[Callable] = None
    ) -> "DecisionTreeBuilder":
        """Agrega un gate a un nodo."""
        if node_id not in self.all_nodes:
            raise ValueError(f"Nodo {node_id} no existe")
        
        node = self.all_nodes[node_id]
        gate = Gate(gate_id, gate_type, description, condition_func)
        node.add_gate(gate)
        
        return self
    
    def connect_nodes(
        self,
        from_node_id: str,
        to_node_id_success: str,
        to_node_id_failure: Optional[str] = None
    ) -> "DecisionTreeBuilder":
        """Conecta nodos."""
        if from_node_id not in self.all_nodes:
            raise ValueError(f"Nodo origen {from_node_id} no existe")
        if to_node_id_success not in self.all_nodes:
            raise ValueError(f"Nodo destino success {to_node_id_success} no existe")
        if to_node_id_failure and to_node_id_failure not in self.all_nodes:
            raise ValueError(f"Nodo destino failure {to_node_id_failure} no existe")
        
        from_node = self.all_nodes[from_node_id]
        from_node.set_success_path(self.all_nodes[to_node_id_success])
        
        if to_node_id_failure:
            from_node.set_failure_path(self.all_nodes[to_node_id_failure])
        
        return self
    
    def build(self) -> DecisionNode:
        """Construye y retorna el árbol."""
        if self.root_node is None:
            raise ValueError("No hay nodo raíz. Crear nodos primero.")
        
        logger.info(f"Árbol construido: {len(self.all_nodes)} nodos")
        return self.root_node
    
    def get_node(self, node_id: str) -> Optional[DecisionNode]:
        """Obtiene un nodo por ID."""
        return self.all_nodes.get(node_id)
    
    def get_all_nodes(self) -> Dict[str, DecisionNode]:
        """Retorna todos los nodos."""
        return self.all_nodes.copy()


def create_standard_decision_tree() -> DecisionTreeBuilder:
    """Crea el árbol de decisión estándar SPM con 12 vías."""
    builder = DecisionTreeBuilder()
    
    # NODO 1: Stock Local (Liberación simple)
    node_1 = builder.create_node(
        "node_1",
        SourceRoute.STOCK_LOCAL,
        "Stock Local",
        "Liberar stock local disponible",
        lead_time=1,
        cost=10,
        success_rate=0.95
    )
    builder.add_gate_to_node(
        "node_1", "gate_stock_available",
        GateType.AVAILABILITY,
        "Stock disponible en almacén"
    )
    
    # NODO 2: Stock Local + Assets
    node_2 = builder.create_node(
        "node_2",
        SourceRoute.STOCK_LOCAL_ASSETS,
        "Stock Local + Assets",
        "Liberar stock con activos",
        lead_time=2,
        cost=15,
        success_rate=0.85
    )
    builder.add_gate_to_node(
        "node_2", "gate_assets_available",
        GateType.AVAILABILITY,
        "Assets disponibles"
    )
    
    # NODO 3: Desarme
    node_3 = builder.create_node(
        "node_3",
        SourceRoute.DISASSEMBLY,
        "Desarme",
        "Desmontar BOM para obtener componentes",
        lead_time=3,
        cost=25,
        success_rate=0.70
    )
    builder.add_gate_to_node(
        "node_3", "gate_bom_available",
        GateType.AVAILABILITY,
        "BOM disponible para desmontar"
    )
    
    # NODO 4: Sustitutos
    node_4 = builder.create_node(
        "node_4",
        SourceRoute.SUBSTITUTES,
        "Sustitutos",
        "Usar equivalencias de proveedores",
        lead_time=2,
        cost=20,
        success_rate=0.75
    )
    builder.add_gate_to_node(
        "node_4", "gate_substitutes_approved",
        GateType.QUALITY,
        "Sustitutos aprobados técnicamente"
    )
    
    # NODO 5: Recupero
    node_5 = builder.create_node(
        "node_5",
        SourceRoute.RECOVERY,
        "Recupero",
        "Reciclaje/desmontaje de activos",
        lead_time=4,
        cost=30,
        success_rate=0.60
    )
    builder.add_gate_to_node(
        "node_5", "gate_recovery_viable",
        GateType.COST,
        "Recupero es viable económicamente"
    )
    
    # NODO 6: Transferencia
    node_6 = builder.create_node(
        "node_6",
        SourceRoute.TRANSFER,
        "Transferencia",
        "Transferencia desde otro centro",
        lead_time=3,
        cost=35,
        success_rate=0.80
    )
    builder.add_gate_to_node(
        "node_6", "gate_transfer_available",
        GateType.AVAILABILITY,
        "Stock disponible en otro centro"
    )
    
    # NODO 7: Intercompañía
    node_7 = builder.create_node(
        "node_7",
        SourceRoute.INTERCOMPANY,
        "Intercompañía",
        "Compra a empresa relacionada",
        lead_time=5,
        cost=45,
        success_rate=0.75
    )
    builder.add_gate_to_node(
        "node_7", "gate_intercompany_available",
        GateType.RELATIONSHIP,
        "Relación intercompañía activa"
    )
    
    # NODO 8: VMI
    node_8 = builder.create_node(
        "node_8",
        SourceRoute.VMI,
        "VMI",
        "Vendor-Managed Inventory",
        lead_time=7,
        cost=40,
        success_rate=0.70
    )
    builder.add_gate_to_node(
        "node_8", "gate_vmi_active",
        GateType.RELATIONSHIP,
        "Contrato VMI vigente"
    )
    
    # NODO 9: Préstamo
    node_9 = builder.create_node(
        "node_9",
        SourceRoute.LOAN,
        "Préstamo",
        "Préstamo de partners/competitors",
        lead_time=2,
        cost=50,
        success_rate=0.50
    )
    builder.add_gate_to_node(
        "node_9", "gate_loan_partner_available",
        GateType.RELATIONSHIP,
        "Partner disponible para préstamo"
    )
    
    # NODO 10: Acelerar
    node_10 = builder.create_node(
        "node_10",
        SourceRoute.EXPEDITE,
        "Acelerar",
        "Rush delivery / Air freight",
        lead_time=1,
        cost=100,
        success_rate=0.85
    )
    builder.add_gate_to_node(
        "node_10", "gate_expedite_available",
        GateType.TIMING,
        "Proveedor acepta expeditar"
    )
    builder.add_gate_to_node(
        "node_10", "gate_expedite_budget",
        GateType.COST,
        "Presupuesto disponible para rush"
    )
    
    # NODO 11: Compra
    node_11 = builder.create_node(
        "node_11",
        SourceRoute.PURCHASE,
        "Compra",
        "Compra a proveedor standard",
        lead_time=14,
        cost=50,
        success_rate=0.95
    )
    builder.add_gate_to_node(
        "node_11", "gate_supplier_available",
        GateType.AVAILABILITY,
        "Proveedor disponible"
    )
    
    # NODO 12: Resultado Final
    node_12 = builder.create_node(
        "node_12",
        SourceRoute.FINAL_RESULT,
        "Resultado Final",
        "Evaluación final de viabilidad",
        lead_time=0,
        cost=0,
        success_rate=1.0
    )
    
    # Conectar nodos según flujo SPM
    builder.connect_nodes("node_1", "node_2", "node_3")
    builder.connect_nodes("node_2", "node_3", "node_4")
    builder.connect_nodes("node_3", "node_4", "node_5")
    builder.connect_nodes("node_4", "node_5", "node_6")
    builder.connect_nodes("node_5", "node_6", "node_7")
    builder.connect_nodes("node_6", "node_8", "node_7")
    builder.connect_nodes("node_7", "node_8", "node_9")
    builder.connect_nodes("node_8", "node_9", "node_10")
    builder.connect_nodes("node_9", "node_10", "node_11")
    builder.connect_nodes("node_10", "node_12", "node_12")
    builder.connect_nodes("node_11", "node_12", "node_12")
    
    return builder
