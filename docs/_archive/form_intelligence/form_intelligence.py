"""
FormIntelligence Service - Sistema IA para formularios inteligentes.

Proporciona:
- Consumo histórico (centro/almacén/todos)
- Stock actual y alternativas
- Estado MRP y status
- Solicitudes en curso
- Validaciones inteligentes
- Sugerencias contextuales
"""

import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
from ..core.db import get_connection


class MaterialConsumptionAnalyzer:
    """Analiza consumo histórico de materiales por centro/almacén."""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.row_factory = sqlite3.Row

    def get_consumption_history(
        self,
        material_codigo: str,
        centro: Optional[str] = None,
        almacen: Optional[str] = None,
        days: int = 90,
    ) -> Dict[str, Any]:
        """
        Obtiene consumo histórico del material.
        
        Args:
            material_codigo: Código del material
            centro: Centro específico (opcional)
            almacen: Almacén específico (opcional)
            days: Días históricos a analizar
        
        Returns:
            Dict con estadísticas de consumo
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        query = """
            SELECT
                s.centro,
                s.almacen_virtual,
                SUM(CAST(json_extract(item.value, '$.cantidad') AS REAL)) AS total_qty,
                COUNT(DISTINCT s.id) AS num_solicitudes,
                AVG(CAST(json_extract(item.value, '$.cantidad') AS REAL)) AS avg_qty,
                MAX(s.created_at) AS last_request
            FROM solicitudes s
            JOIN json_each(s.data_json, '$.items') AS item
            WHERE s.status NOT IN ('draft', 'cancelled')
                AND s.created_at >= ?
                AND json_extract(item.value, '$.codigo') = ?
        """
        params = [cutoff_date, material_codigo]

        if centro:
            query += " AND s.centro = ?"
            params.append(centro)

        if almacen:
            query += " AND s.almacen_virtual = ?"
            params.append(almacen)

        query += " GROUP BY s.centro, s.almacen_virtual"

        try:
            rows = self.con.execute(query, params).fetchall()

            if centro and almacen:
                # Específico: centro + almacén
                row = rows[0] if rows else None
                if row:
                    return {
                        "consumo_total": (row["total_qty"] or 0),
                        "solicitudes": row["num_solicitudes"] or 0,
                        "consumo_promedio": (row["avg_qty"] or 0),
                        "ultimo_consumo": row["last_request"],
                        "periodo_dias": days,
                        "nivel": self._classify_consumption(row["total_qty"] or 0, days),
                    }
                return {
                    "consumo_total": 0,
                    "solicitudes": 0,
                    "consumo_promedio": 0,
                    "ultimo_consumo": None,
                    "periodo_dias": days,
                    "nivel": "Sin consumo",
                }
            else:
                # Agregado por centro/almacén
                results = {}
                for row in rows:
                    key = f"{row['centro']}/{row['almacen_virtual']}"
                    results[key] = {
                        "consumo_total": row["total_qty"] or 0,
                        "solicitudes": row["num_solicitudes"] or 0,
                        "consumo_promedio": row["avg_qty"] or 0,
                        "ultimo_consumo": row["last_request"],
                        "periodo_dias": days,
                        "nivel": self._classify_consumption(row["total_qty"] or 0, days),
                    }
                return results
        except Exception as e:
            print(f"Error analyzing consumption: {e}")
            return {}

    @staticmethod
    def _classify_consumption(qty: float, days: int) -> str:
        """Clasifica nivel de consumo."""
        if qty == 0:
            return "Sin consumo"
        daily_rate = qty / days
        if daily_rate > 1:
            return "Alto"
        elif daily_rate > 0.1:
            return "Medio"
        else:
            return "Bajo"


class StockAnalyzer:
    """Analiza stock actual y alternativas."""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.row_factory = sqlite3.Row

    def get_stock_status(
        self, material_codigo: str, centro: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estado del stock del material.
        
        Nota: Esta es una estructura simulada. En producción,
        necesitarías una tabla de stock real o integración con SAP.
        """
        try:
            # Simular consulta a tabla de stock
            # En realidad: SELECT * FROM stock WHERE material = ? AND centro = ?
            return {
                "disponible": 150,
                "reservado": 30,
                "disponible_neto": 120,
                "punto_pedido": 100,
                "stock_maximo": 500,
                "estado": "OK",  # OK, BAJO, CRITICO, SOBRESTOCK
                "ubicaciones": [
                    {"almacen": "01", "cantidad": 80, "lote": "LOT001"},
                    {"almacen": "02", "cantidad": 40, "lote": "LOT002"},
                ],
            }
        except Exception as e:
            print(f"Error getting stock: {e}")
            return {"error": str(e)}

    def get_alternative_materials(
        self, material_codigo: str
    ) -> List[Dict[str, Any]]:
        """Obtiene materiales alternativos."""
        try:
            # Simular equivalencias
            return [
                {
                    "codigo": "ALT001",
                    "descripcion": "Material alternativo 1",
                    "similitud": 0.95,
                    "stock": 200,
                    "precio_usd": 45.50,
                    "razon": "Compatible con especificaciones técnicas",
                }
            ]
        except Exception as e:
            print(f"Error getting alternatives: {e}")
            return []


class MRPAnalyzer:
    """Analiza estado MRP del material."""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.row_factory = sqlite3.Row

    def get_mrp_status(
        self, material_codigo: str, centro: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estado MRP del material.
        
        Estados posibles:
        - STOCK_OK: Stock disponible
        - STOCK_BAJO: Por debajo de punto de pedido
        - SOBRESTOCK: Arriba de stock máximo
        - PEDIDO_CURSO: Hay PO en curso
        - MRP_PLANIFICADO: MRP propone compra
        """
        try:
            # Simular estado MRP
            return {
                "estado": "STOCK_OK",
                "stock_actual": 250,
                "punto_pedido": 100,
                "stock_maximo": 500,
                "consumo_mensual": 120,
                "lead_time_dias": 15,
                "proxima_reorden": None,
                "pedidos_curso": 0,
                "fecha_proximo_pedido": None,
                "observaciones": "Stock estable, reorden previsto en 30 días",
            }
        except Exception as e:
            print(f"Error getting MRP status: {e}")
            return {}


class SolicitudAnalyzer:
    """Analiza solicitudes en curso del mismo material."""

    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.con.row_factory = sqlite3.Row

    def get_pending_solicitudes(
        self, material_codigo: str
    ) -> List[Dict[str, Any]]:
        """Obtiene solicitudes en curso para el mismo material."""
        try:
            query = """
                SELECT
                    s.id,
                    s.id_usuario,
                    s.centro,
                    s.criticidad,
                    s.status,
                    s.created_at,
                    json_extract(item.value, '$.cantidad') as cantidad
                FROM solicitudes s
                JOIN json_each(s.data_json, '$.items') AS item
                WHERE s.status NOT IN ('draft', 'cancelled', 'completed')
                    AND json_extract(item.value, '$.codigo') = ?
                ORDER BY s.created_at DESC
                LIMIT 5
            """
            rows = self.con.execute(query, (material_codigo,)).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting pending solicitudes: {e}")
            return []


class FormIntelligenceEngine:
    """Motor principal de inteligencia para formularios."""

    def __init__(self):
        self.con = None

    def _init_connection(self):
        """Inicializa conexión a BD."""
        if not self.con:
            self.con = get_connection()

    def analyze_material(
        self,
        material_codigo: str,
        cantidad: float,
        centro: Optional[str] = None,
        almacen: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Análisis completo de un material para decisiones inteligentes.
        
        Returns:
            Dict con insights y sugerencias
        """
        self._init_connection()

        consumption_analyzer = MaterialConsumptionAnalyzer(self.con)
        stock_analyzer = StockAnalyzer(self.con)
        mrp_analyzer = MRPAnalyzer(self.con)
        solicitud_analyzer = SolicitudAnalyzer(self.con)

        consumption = consumption_analyzer.get_consumption_history(
            material_codigo, centro, almacen, days=90
        )
        stock = stock_analyzer.get_stock_status(material_codigo, centro)
        alternatives = stock_analyzer.get_alternative_materials(material_codigo)
        mrp_status = mrp_analyzer.get_mrp_status(material_codigo, centro)
        pending_solicitudes = solicitud_analyzer.get_pending_solicitudes(
            material_codigo
        )

        # Calcular scores y sugerencias
        analysis = {
            "material_codigo": material_codigo,
            "cantidad_solicitada": cantidad,
            "timestamp": datetime.now().isoformat(),
            "consumo_historico": consumption,
            "stock_actual": stock,
            "materiales_alternativos": alternatives,
            "estado_mrp": mrp_status,
            "solicitudes_en_curso": pending_solicitudes,
            "sugerencias": self._generate_suggestions(
                material_codigo,
                cantidad,
                consumption,
                stock,
                mrp_status,
                pending_solicitudes,
            ),
            "alertas": self._generate_alerts(
                material_codigo, cantidad, stock, mrp_status, pending_solicitudes
            ),
            "confianza": 0.92,
        }

        return analysis

    @staticmethod
    def _generate_suggestions(
        material_codigo: str,
        cantidad: float,
        consumption: Dict,
        stock: Dict,
        mrp_status: Dict,
        pending_solicitudes: List,
    ) -> List[Dict[str, Any]]:
        """Genera sugerencias inteligentes."""
        suggestions = []

        # Sugerencia 1: Stock vs Consumo
        if isinstance(consumption, dict) and "consumo_promedio" in consumption:
            monthly_consumption = consumption.get("consumo_promedio", 0) * 30
            if cantidad > monthly_consumption * 2:
                suggestions.append(
                    {
                        "tipo": "CANTIDAD_ALTA",
                        "titulo": "Cantidad por encima del consumo típico",
                        "mensaje": f"Consumo promedio mensual: {monthly_consumption:.2f} UN. Solicitando: {cantidad} UN",
                        "prioridad": "advertencia",
                        "accion": "Revisar si es necesario tanto stock",
                    }
                )

        # Sugerencia 2: Split Stock/Compra
        stock_disponible = stock.get("disponible_neto", 0)
        if stock_disponible > 0 and stock_disponible < cantidad:
            suggestions.append(
                {
                    "tipo": "SPLIT_STOCK_COMPRA",
                    "titulo": "Split sugerido",
                    "mensaje": f"Stock disponible: {stock_disponible} UN. Sugerir {stock_disponible} UN de stock + {cantidad - stock_disponible} UN de compra",
                    "prioridad": "info",
                    "accion": "split",
                    "payload": {
                        "stock_cantidad": stock_disponible,
                        "compra_cantidad": cantidad - stock_disponible,
                    },
                }
            )

        # Sugerencia 3: Alternativas disponibles
        if stock.get("estado") == "BAJO" and len([]):  # alternatives > 0
            suggestions.append(
                {
                    "tipo": "ALTERNATIVAS_DISPONIBLES",
                    "titulo": "Considera alternativas con mejor stock",
                    "mensaje": "Material con stock bajo, pero hay alternativas disponibles",
                    "prioridad": "sugerencia",
                }
            )

        # Sugerencia 4: MRP Status
        if mrp_status.get("estado") == "PEDIDO_CURSO":
            suggestions.append(
                {
                    "tipo": "PEDIDO_EN_CURSO",
                    "titulo": "Hay compra MRP en curso",
                    "mensaje": f"MRP ya planificó compra. Revisar antes de generar nueva solicitud",
                    "prioridad": "advertencia",
                }
            )

        # Sugerencia 5: Solicitudes duplicadas
        if len(pending_solicitudes) > 0:
            total_qty = sum(s.get("cantidad", 0) for s in pending_solicitudes)
            suggestions.append(
                {
                    "tipo": "SOLICITUDES_DUPLICADAS",
                    "titulo": "Material ya solicitado",
                    "mensaje": f"{len(pending_solicitudes)} solicitudes en curso para este material ({total_qty} UN total)",
                    "prioridad": "advertencia",
                    "links": [{"id": s["id"], "estado": s["status"]} for s in pending_solicitudes[:3]],
                }
            )

        return suggestions

    @staticmethod
    def _generate_alerts(
        material_codigo: str,
        cantidad: float,
        stock: Dict,
        mrp_status: Dict,
        pending_solicitudes: List,
    ) -> List[Dict[str, Any]]:
        """Genera alertas críticas."""
        alerts = []

        # Alerta 1: Stock crítico
        if stock.get("estado") == "CRITICO":
            alerts.append(
                {
                    "tipo": "STOCK_CRITICO",
                    "mensaje": "STOCK CRÍTICO: Coordinar urgentemente con planificador",
                    "severidad": "critica",
                }
            )

        # Alerta 2: Sobrestock
        if stock.get("estado") == "SOBRESTOCK":
            alerts.append(
                {
                    "tipo": "SOBRESTOCK",
                    "mensaje": "Material en SOBRESTOCK. Revisar si es necesaria esta compra",
                    "severidad": "advertencia",
                }
            )

        return alerts

    def get_chat_context(self, material_codigo: str) -> str:
        """Prepara contexto para chat IA."""
        analysis = self.analyze_material(material_codigo, 0)
        
        context = f"""
Material: {material_codigo}
Consumo últimos 90 días: {analysis['consumo_historico'].get('consumo_total', 0)} UN
Stock actual: {analysis['stock_actual'].get('disponible_neto', 0)} UN
Estado MRP: {analysis['estado_mrp'].get('estado', 'Desconocido')}
Solicitudes en curso: {len(analysis['solicitudes_en_curso'])}

Alertas: {len(analysis['alertas'])}
Sugerencias: {len(analysis['sugerencias'])}
        """
        return context


# Singleton
_form_intelligence = None


def get_form_intelligence_engine() -> FormIntelligenceEngine:
    """Retorna instancia singleton del motor."""
    global _form_intelligence
    if _form_intelligence is None:
        _form_intelligence = FormIntelligenceEngine()
    return _form_intelligence
