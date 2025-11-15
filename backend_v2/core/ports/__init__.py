"""
Backend v2.0 - Core Ports Package

Contiene las interfaces (ports) que definen contratos para servicios externos.
Sigue arquitectura hexagonal (Ports & Adapters).
"""

from .planner_port import PlannerPort, SourcingPath, OptimizationStrategy

__all__ = [
    "PlannerPort",
    "SourcingPath",
    "OptimizationStrategy",
]
