"""
Optimización de portafolio (Nivel 3)
Formulación MIP/ILP con PuLP.

Módulos:
- constraint_builder: Construcción de restricciones
- formulation: Formulación MIP y modelo de optimización
- solver_manager: Solver con estrategias (exact, greedy, greedy+reopt)
- model_analyzer: Post-optimización y análisis
"""

# Importar constraint_builder
from .constraint_builder import (
    ConstraintBuilder,
    ConstraintSet,
    ConstraintType,
    DemandConstraint,
    FEFOConstraint,
    CapacityConstraint,
    LeadTimeConstraint,
    ServiceLevelConstraint,
    TransferConstraint,
    OneInConstraint,
    BudgetConstraint,
    SourcingPreferenceConstraint
)

# Importar formulation
from .formulation import (
    OptimizationModel,
    SolutionAnalyzer,
    SolverStatus,
    PortfolioVariable
)

# Importar solver_manager
from .solver_manager import (
    SolverManager,
    SolverConfig,
    SolverResult,
    SolverStrategy,
    GreedySolver,
    LocalSearchOptimizer
)

# Importar model_analyzer
from .model_analyzer import (
    ModelAnalyzer,
    SensitivityAnalysis,
    ViabilityReport,
    CostBreakdownReport,
    RobustnessAnalyzer
)

__all__ = [
    # constraint_builder
    "ConstraintBuilder",
    "ConstraintSet",
    "ConstraintType",
    "DemandConstraint",
    "FEFOConstraint",
    "CapacityConstraint",
    "LeadTimeConstraint",
    "ServiceLevelConstraint",
    "TransferConstraint",
    "OneInConstraint",
    "BudgetConstraint",
    "SourcingPreferenceConstraint",
    
    # formulation
    "OptimizationModel",
    "SolutionAnalyzer",
    "SolverStatus",
    "PortfolioVariable",
    
    # solver_manager
    "SolverManager",
    "SolverConfig",
    "SolverResult",
    "SolverStrategy",
    "GreedySolver",
    "LocalSearchOptimizer",
    
    # model_analyzer
    "ModelAnalyzer",
    "SensitivityAnalysis",
    "ViabilityReport",
    "CostBreakdownReport",
    "RobustnessAnalyzer"
]
