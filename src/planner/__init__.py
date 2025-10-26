"""
Supply Chain Planning Engine (SCPE)
Motor de optimización de abastecimiento con:
- Análisis técnico-legal
- Scoring probabilístico
- Optimización de portafolio (MIP/ILP)
- Árbol de decisión con gates operacionales
"""

__version__ = "1.0.0"
__author__ = "Manuel Remon"

from . import models
from . import filters
from . import scoring
from . import optimization
from . import rules
from . import events

__all__ = [
    "models",
    "filters",
    "scoring",
    "optimization", 
    "rules",
    "events",
]
