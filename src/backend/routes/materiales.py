from __future__ import annotations
from flask import Blueprint, request
from ..core.db import get_connection
from ..models.schemas import MaterialSearchQuery

bp = Blueprint("materiales", __name__, url_prefix="/api")

@bp.get("/materiales")
def search_materiales():
    params = MaterialSearchQuery(**request.args.to_dict())
    clauses: list[str] = []
    args: list[str] = []

    if params.codigo:
        # Usar búsqueda de prefijo para códigos, es más rápido y relevante.
        like_code = f"{params.codigo}%"
        clauses.append("codigo LIKE ?")
        args.append(like_code)
    
    if params.descripcion:
        like_desc = f"%{params.descripcion}%"
        clauses.append("descripcion LIKE ?")
        args.append(like_desc)

    if params.q:
        like_any = f"%{params.q}%"
        clauses.append("(codigo LIKE ? OR descripcion LIKE ?)")
        args.extend([like_any, like_any])

    if not clauses:
        # Si no hay filtros, devolver todos (limitados)
        where = "1=1"
    else:
        where = " AND ".join(clauses)
    limit = params.limit

    with get_connection() as con:
        cur = con.execute(
            f"""
            SELECT codigo, descripcion, descripcion_larga, unidad, precio_usd
            FROM materiales
            WHERE {where}
            ORDER BY descripcion, codigo
            LIMIT ?
            """, (*args, limit)
        )
        return [dict(r) for r in cur.fetchall()]