"""
Servicio de lógica de negocio para Solicitudes
Maneja CRUD de solicitudes, items, y validaciones de negocio
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session, joinedload

from core.db import get_db
from models.solicitud import Solicitud, SolicitudItem, Aprobacion, Material
from models.user import User


class SolicitudService:
    """Servicio para manejo de solicitudes"""

    @staticmethod
    def create_solicitud(user_id: str, data: Dict[str, Any]) -> Solicitud:
        """
        Crea una nueva solicitud con sus items
        
        Args:
            user_id: ID del usuario solicitante
            data: Datos de la solicitud (centro, sector, items, etc.)
        
        Returns:
            Solicitud creada
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        with get_db() as db:
            # Validar que el usuario existe
            user = db.query(User).filter(User.username == user_id).first()
            if not user:
                raise ValueError(f"Usuario {user_id} no encontrado")
            
            # Validar items
            items_data = data.get("items", [])
            if not items_data:
                raise ValueError("La solicitud debe tener al menos un item")
            
            # Validar que todos los materiales existen
            material_codigos = [item["material_codigo"] for item in items_data]
            materiales = db.query(Material).filter(Material.codigo.in_(material_codigos)).all()
            materiales_dict = {m.codigo: m for m in materiales}
            
            missing_materials = set(material_codigos) - set(materiales_dict.keys())
            if missing_materials:
                raise ValueError(f"Materiales no encontrados: {', '.join(missing_materials)}")
            
            # Calcular total
            total_monto = 0.0
            for item_data in items_data:
                cantidad = item_data.get("cantidad", 0)
                precio = item_data.get("precio_unitario")
                if precio is None:
                    # Usar precio del catálogo si no viene especificado
                    material = materiales_dict[item_data["material_codigo"]]
                    precio = material.precio_usd
                    item_data["precio_unitario"] = precio
                total_monto += cantidad * precio
            
            # Crear solicitud
            solicitud = Solicitud(
                id_usuario=user_id,
                centro=data["centro"],
                sector=data.get("sector", "General"),
                justificacion=data["justificacion"],
                centro_costos=data.get("centro_costos"),
                almacen_virtual=data.get("almacen_virtual"),
                criticidad=data.get("criticidad", "Normal"),
                fecha_necesidad=data.get("fecha_necesidad"),
                status="pendiente_de_aprobacion",
                total_monto=round(total_monto, 2),
            )
            
            db.add(solicitud)
            db.flush()  # Para obtener el ID
            
            # Crear items
            for item_data in items_data:
                item = SolicitudItem(
                    solicitud_id=solicitud.id,
                    material_codigo=item_data["material_codigo"],
                    cantidad=item_data["cantidad"],
                    precio_unitario=item_data["precio_unitario"],
                    comentario=item_data.get("comentario"),
                )
                db.add(item)
            
            db.commit()
            db.refresh(solicitud)
            
            # Recargar con items eager-loaded antes de expunge
            solicitud = db.query(Solicitud).options(joinedload(Solicitud.items)).filter(Solicitud.id == solicitud.id).first()
            db.expunge(solicitud)
            
            return solicitud

    @staticmethod
    def create_draft(user_id: str, data: Dict[str, Any]) -> Solicitud:
        """
        Crea un borrador de solicitud (sin items obligatorios)
        
        Args:
            user_id: ID del usuario
            data: Datos parciales de la solicitud
        
        Returns:
            Solicitud en estado draft
        """
        with get_db() as db:
            solicitud = Solicitud(
                id_usuario=user_id,
                centro=data.get("centro", ""),
                sector=data.get("sector", ""),
                justificacion=data.get("justificacion", ""),
                centro_costos=data.get("centro_costos"),
                almacen_virtual=data.get("almacen_virtual"),
                criticidad=data.get("criticidad", "Normal"),
                fecha_necesidad=data.get("fecha_necesidad"),
                status="draft",
                total_monto=0.0,
            )
            
            db.add(solicitud)
            db.commit()
            db.refresh(solicitud)
            
            # Recargar con items eager-loaded antes de expunge
            solicitud = db.query(Solicitud).options(joinedload(Solicitud.items)).filter(Solicitud.id == solicitud.id).first()
            db.expunge(solicitud)
            
            return solicitud

    @staticmethod
    def get_solicitud_by_id(solicitud_id: int) -> Optional[Solicitud]:
        """Obtiene una solicitud por ID con sus items"""
        with get_db() as db:
            solicitud = db.query(Solicitud).options(joinedload(Solicitud.items)).filter(Solicitud.id == solicitud_id).first()
            if solicitud:
                db.expunge(solicitud)
            return solicitud

    @staticmethod
    def list_solicitudes(
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        """
        Lista solicitudes con filtros y paginación
        
        Args:
            user_id: Filtrar por usuario (None = todas)
            status: Filtrar por estado
            page: Página actual
            per_page: Items por página
        
        Returns:
            Dict con solicitudes, total, page, per_page
        """
        with get_db() as db:
            query = db.query(Solicitud).options(joinedload(Solicitud.items))
            
            # Filtros
            if user_id:
                query = query.filter(Solicitud.id_usuario == user_id)
            if status:
                query = query.filter(Solicitud.status == status)
            
            # Contar total
            total = query.count()
            
            # Paginación
            offset = (page - 1) * per_page
            solicitudes = query.order_by(desc(Solicitud.created_at)).offset(offset).limit(per_page).all()
            
            # Expunge solo solicitudes (items se expungen automáticamente)
            for sol in solicitudes:
                db.expunge(sol)
            
            return {
                "solicitudes": solicitudes,
                "total": total,
                "page": page,
                "per_page": per_page,
            }

    @staticmethod
    def update_solicitud(solicitud_id: int, data: Dict[str, Any]) -> Solicitud:
        """
        Actualiza una solicitud existente
        
        Args:
            solicitud_id: ID de la solicitud
            data: Datos a actualizar
        
        Returns:
            Solicitud actualizada
        
        Raises:
            ValueError: Si la solicitud no existe o no se puede modificar
        """
        with get_db() as db:
            solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
            if not solicitud:
                raise ValueError(f"Solicitud {solicitud_id} no encontrada")
            
            # Solo permitir actualizar borradores o pendientes
            if solicitud.status not in ["draft", "pendiente_de_aprobacion"]:
                raise ValueError(f"No se puede modificar una solicitud en estado {solicitud.status}")
            
            # Actualizar campos
            if "centro" in data:
                solicitud.centro = data["centro"]
            if "sector" in data:
                solicitud.sector = data["sector"]
            if "justificacion" in data:
                solicitud.justificacion = data["justificacion"]
            if "centro_costos" in data:
                solicitud.centro_costos = data["centro_costos"]
            if "almacen_virtual" in data:
                solicitud.almacen_virtual = data["almacen_virtual"]
            if "criticidad" in data:
                solicitud.criticidad = data["criticidad"]
            if "fecha_necesidad" in data:
                solicitud.fecha_necesidad = data["fecha_necesidad"]
            
            # Si hay items, recalcular total
            if "items" in data:
                # Eliminar items existentes
                db.query(SolicitudItem).filter(SolicitudItem.solicitud_id == solicitud_id).delete()
                
                # Validar materiales
                items_data = data["items"]
                material_codigos = [item["material_codigo"] for item in items_data]
                materiales = db.query(Material).filter(Material.codigo.in_(material_codigos)).all()
                materiales_dict = {m.codigo: m for m in materiales}
                
                missing = set(material_codigos) - set(materiales_dict.keys())
                if missing:
                    raise ValueError(f"Materiales no encontrados: {', '.join(missing)}")
                
                # Crear nuevos items
                total_monto = 0.0
                for item_data in items_data:
                    cantidad = item_data["cantidad"]
                    precio = item_data.get("precio_unitario")
                    if precio is None:
                        material = materiales_dict[item_data["material_codigo"]]
                        precio = material.precio_usd
                    
                    item = SolicitudItem(
                        solicitud_id=solicitud_id,
                        material_codigo=item_data["material_codigo"],
                        cantidad=cantidad,
                        precio_unitario=precio,
                        comentario=item_data.get("comentario"),
                    )
                    db.add(item)
                    total_monto += cantidad * precio
                
                solicitud.total_monto = round(total_monto, 2)
            
            solicitud.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(solicitud)
            
            # Recargar con items eager-loaded antes de expunge
            solicitud = db.query(Solicitud).options(joinedload(Solicitud.items)).filter(Solicitud.id == solicitud.id).first()
            db.expunge(solicitud)
            
            return solicitud

    @staticmethod
    def aprobar_solicitud(solicitud_id: int, aprobador_id: str, comentario: Optional[str] = None) -> Solicitud:
        """
        Aprueba una solicitud
        
        Args:
            solicitud_id: ID de la solicitud
            aprobador_id: ID del aprobador
            comentario: Comentario opcional
        
        Returns:
            Solicitud aprobada
        """
        with get_db() as db:
            solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
            if not solicitud:
                raise ValueError(f"Solicitud {solicitud_id} no encontrada")
            
            if solicitud.status != "pendiente_de_aprobacion":
                raise ValueError(f"La solicitud debe estar en estado pendiente_de_aprobacion")
            
            # Crear registro de aprobación
            aprobacion = Aprobacion(
                solicitud_id=solicitud_id,
                aprobador_id=aprobador_id,
                decision="aprobada",
                comentario=comentario,
            )
            db.add(aprobacion)
            
            # Actualizar estado
            solicitud.status = "aprobada"
            solicitud.aprobador_id = aprobador_id
            solicitud.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(solicitud)
            
            # Recargar con items eager-loaded antes de expunge
            solicitud = db.query(Solicitud).options(joinedload(Solicitud.items)).filter(Solicitud.id == solicitud.id).first()
            db.expunge(solicitud)
            
            return solicitud

    @staticmethod
    def rechazar_solicitud(solicitud_id: int, aprobador_id: str, comentario: Optional[str] = None) -> Solicitud:
        """
        Rechaza una solicitud
        
        Args:
            solicitud_id: ID de la solicitud
            aprobador_id: ID del aprobador
            comentario: Comentario opcional
        
        Returns:
            Solicitud rechazada
        """
        with get_db() as db:
            solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
            if not solicitud:
                raise ValueError(f"Solicitud {solicitud_id} no encontrada")
            
            if solicitud.status != "pendiente_de_aprobacion":
                raise ValueError(f"La solicitud debe estar en estado pendiente_de_aprobacion")
            
            # Crear registro de rechazo
            aprobacion = Aprobacion(
                solicitud_id=solicitud_id,
                aprobador_id=aprobador_id,
                decision="rechazada",
                comentario=comentario,
            )
            db.add(aprobacion)
            
            # Actualizar estado
            solicitud.status = "rechazada"
            solicitud.aprobador_id = aprobador_id
            solicitud.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(solicitud)
            
            # Recargar con items eager-loaded antes de expunge
            solicitud = db.query(Solicitud).options(joinedload(Solicitud.items)).filter(Solicitud.id == solicitud.id).first()
            db.expunge(solicitud)
            
            return solicitud


class MaterialService:
    """Servicio para manejo de materiales"""

    @staticmethod
    def search_materiales(
        q: Optional[str] = None,
        codigo: Optional[str] = None,
        descripcion: Optional[str] = None,
        centro: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 100,
    ) -> List[Material]:
        """
        Busca materiales con filtros
        
        Args:
            q: Búsqueda general (código o descripción)
            codigo: Filtrar por código
            descripcion: Filtrar por descripción
            centro: Filtrar por centro
            sector: Filtrar por sector
            limit: Límite de resultados
        
        Returns:
            Lista de materiales
        """
        with get_db() as db:
            query = db.query(Material)
            
            # Filtros
            if q:
                query = query.filter(
                    or_(
                        Material.codigo.ilike(f"%{q}%"),
                        Material.descripcion.ilike(f"%{q}%"),
                    )
                )
            if codigo:
                query = query.filter(Material.codigo.ilike(f"{codigo}%"))
            if descripcion:
                query = query.filter(Material.descripcion.ilike(f"%{descripcion}%"))
            if centro:
                query = query.filter(Material.centro == centro)
            if sector:
                query = query.filter(Material.sector == sector)
            
            materiales = query.limit(limit).all()
            
            # Expunge
            for material in materiales:
                db.expunge(material)
            
            return materiales

    @staticmethod
    def get_material_by_codigo(codigo: str) -> Optional[Material]:
        """Obtiene un material por código"""
        with get_db() as db:
            material = db.query(Material).filter(Material.codigo == codigo).first()
            if material:
                db.expunge(material)
            return material

    @staticmethod
    def create_material(data: Dict[str, Any]) -> Material:
        """
        Crea un nuevo material
        
        Args:
            data: Datos del material
        
        Returns:
            Material creado
        
        Raises:
            ValueError: Si el código ya existe
        """
        with get_db() as db:
            # Validar que no exista
            existing = db.query(Material).filter(Material.codigo == data["codigo"]).first()
            if existing:
                raise ValueError(f"Material con código {data['codigo']} ya existe")
            
            material = Material(
                codigo=data["codigo"],
                descripcion=data["descripcion"],
                descripcion_larga=data.get("descripcion_larga"),
                unidad=data.get("unidad"),
                precio_usd=data.get("precio_usd", 0.0),
                centro=data.get("centro"),
                sector=data.get("sector"),
            )
            
            db.add(material)
            db.commit()
            db.refresh(material)
            db.expunge(material)
            
            return material

    @staticmethod
    def update_material(codigo: str, data: Dict[str, Any]) -> Material:
        """
        Actualiza un material existente
        
        Args:
            codigo: Código del material
            data: Datos a actualizar
        
        Returns:
            Material actualizado
        
        Raises:
            ValueError: Si el material no existe
        """
        with get_db() as db:
            material = db.query(Material).filter(Material.codigo == codigo).first()
            if not material:
                raise ValueError(f"Material {codigo} no encontrado")
            
            if "descripcion" in data:
                material.descripcion = data["descripcion"]
            if "descripcion_larga" in data:
                material.descripcion_larga = data["descripcion_larga"]
            if "unidad" in data:
                material.unidad = data["unidad"]
            if "precio_usd" in data:
                material.precio_usd = data["precio_usd"]
            if "centro" in data:
                material.centro = data["centro"]
            if "sector" in data:
                material.sector = data["sector"]
            
            db.commit()
            db.refresh(material)
            db.expunge(material)
            
            return material
