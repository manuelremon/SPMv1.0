"""
Filtro técnico-legal (Nivel 1)
Descarta opciones que no cumplen especificaciones, normas, o restricciones.
"""

from .technical_legal import (
    TechnicalLegalFilter,
    FilterResult,
    FilterReason,
)

__all__ = [
    "TechnicalLegalFilter",
    "FilterResult",
    "FilterReason",
]
