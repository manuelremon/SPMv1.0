"""Tests for the Form Intelligence analyzers."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.services.form_intelligence import (
    MaterialConsumptionAnalyzer,
    SolicitudAnalyzer,
)


@pytest.fixture()
def connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute(
        """
        CREATE TABLE solicitudes (
            id INTEGER PRIMARY KEY,
            id_usuario TEXT DEFAULT 'tester',
            centro TEXT,
            criticidad TEXT DEFAULT 'media',
            almacen_virtual TEXT,
            status TEXT,
            created_at TEXT,
            data_json TEXT
        )
        """
    )
    yield con
    con.close()


def _insert_solicitud(con: sqlite3.Connection, **kwargs) -> None:
    payload = {
        "items": kwargs.pop(
            "items",
            [
                {"codigo": "MAT-001", "cantidad": 5},
            ],
        )
    }
    con.execute(
        """
        INSERT INTO solicitudes (centro, almacen_virtual, status, created_at, data_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            kwargs.get("centro", "1000"),
            kwargs.get("almacen_virtual", "A1"),
            kwargs.get("status", "approved"),
            kwargs.get("created_at", datetime.now().isoformat()),
            kwargs.get("data_json", json.dumps(payload)),
        ),
    )
    con.commit()


def test_get_consumption_history_returns_totals(connection: sqlite3.Connection) -> None:
    now = datetime.now()
    items = [
        {"codigo": "MAT-001", "cantidad": 10},
        {"codigo": "OTHER", "cantidad": 1},
    ]
    _insert_solicitud(
        connection,
        centro="1000",
        almacen_virtual="A1",
        created_at=now.isoformat(),
        items=items,
    )
    _insert_solicitud(
        connection,
        centro="1000",
        almacen_virtual="A1",
        created_at=(now - timedelta(days=10)).isoformat(),
        items=[{"codigo": "MAT-001", "cantidad": 5}],
    )

    analyzer = MaterialConsumptionAnalyzer(connection)
    result = analyzer.get_consumption_history("MAT-001", centro="1000", almacen="A1")

    assert result["consumo_total"] == 15
    assert result["solicitudes"] == 2
    assert result["consumo_promedio"] == pytest.approx(7.5)


def test_get_pending_solicitudes_filters_by_material(connection: sqlite3.Connection) -> None:
    _insert_solicitud(
        connection,
        centro="1000",
        almacen_virtual="A1",
        status="pending",
        items=[{"codigo": "MAT-001", "cantidad": 3}],
    )
    _insert_solicitud(
        connection,
        centro="1000",
        almacen_virtual="A1",
        status="pending",
        items=[{"codigo": "OTHER", "cantidad": 4}],
    )

    analyzer = SolicitudAnalyzer(connection)
    results = analyzer.get_pending_solicitudes("MAT-001")

    assert len(results) == 1
    assert float(results[0]["cantidad"]) == 3


def test_get_consumption_history_empty_returns_defaults(connection: sqlite3.Connection) -> None:
    analyzer = MaterialConsumptionAnalyzer(connection)
    result = analyzer.get_consumption_history("MAT-404", centro="1000", almacen="A1")

    assert result == {
        "consumo_total": 0,
        "solicitudes": 0,
        "consumo_promedio": 0,
        "ultimo_consumo": None,
        "periodo_dias": 90,
        "nivel": "Sin consumo",
    }
