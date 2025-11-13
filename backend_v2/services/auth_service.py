"""
Backend v2.0 - Authentication Service
Lógica de negocio para autenticación con modelos User reales
"""
from __future__ import annotations

from typing import Optional

import bcrypt
from sqlalchemy.orm import Session

from core.db import get_db
from models.user import User


class AuthService:
    """Servicio de autenticación con database real"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash de contraseña con bcrypt.
        
        Args:
            password: Contraseña en texto plano
        
        Returns:
            Hash bcrypt como string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    @staticmethod
    def verify_password(password_hash: str, candidate: str) -> bool:
        """
        Verifica contraseña contra hash bcrypt.
        
        Args:
            password_hash: Hash bcrypt almacenado
            candidate: Contraseña a verificar
        
        Returns:
            True si coincide, False si no
        """
        try:
            return bcrypt.checkpw(
                candidate.encode("utf-8"),
                password_hash.encode("utf-8")
            )
        except Exception:
            return False
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Obtiene usuario por ID numérico.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Usuario o None si no existe
        """
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # Eager load para evitar DetachedInstanceError
                db.expunge(user)
            return user
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Obtiene usuario por username (id_spm).
        Búsqueda case-insensitive.
        
        Args:
            username: Username, email o id_spm
        
        Returns:
            Usuario o None si no existe
        """
        username_lower = username.lower().strip()
        
        with get_db() as db:
            # Buscar por username o email
            user = (
                db.query(User)
                .filter(
                    (User.username == username_lower) |
                    (User.email == username_lower)
                )
                .first()
            )
            if user:
                # Eager load para evitar DetachedInstanceError
                db.expunge(user)
            return user
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Autentica usuario con username/password.
        
        Compatible con v1.0:
        - Búsqueda por username o email
        - Case-insensitive
        - Verifica password con bcrypt
        
        Args:
            username: Username, email o id_spm
            password: Contraseña en texto plano
        
        Returns:
            Usuario si credenciales válidas, None si no
        """
        if not username or not password:
            return None
        
        user = AuthService.get_user_by_username(username)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not AuthService.verify_password(user.password_hash, password):
            return None
        
        return user
    
    @staticmethod
    def create_user(
        username: str,
        password: str,
        nombre: str,
        apellido: str,
        role: str = "Solicitante",
        email: Optional[str] = None,
        **kwargs
    ) -> User:
        """
        Crea un nuevo usuario.
        
        Args:
            username: ID SPM del usuario
            password: Contraseña en texto plano
            nombre: Nombre
            apellido: Apellido
            role: Rol (default: Solicitante)
            email: Email (opcional)
            **kwargs: Campos adicionales (sector, posicion, etc.)
        
        Returns:
            Usuario creado
        
        Raises:
            ValueError: Si username ya existe
        """
        username_lower = username.lower().strip()
        
        with get_db() as db:
            # Verificar si ya existe
            existing = db.query(User).filter(User.username == username_lower).first()
            if existing:
                raise ValueError(f"Usuario '{username}' ya existe")
            
            # Crear usuario
            user = User(
                username=username_lower,
                password_hash=AuthService.hash_password(password),
                nombre=nombre,
                apellido=apellido,
                role=role,
                email=email.lower() if email else None,
                sector=kwargs.get("sector"),
                posicion=kwargs.get("posicion"),
                centros=kwargs.get("centros"),
                telefono=kwargs.get("telefono"),
                id_ypf=kwargs.get("id_ypf"),
                jefe=kwargs.get("jefe"),
                gerente1=kwargs.get("gerente1"),
                gerente2=kwargs.get("gerente2"),
                is_active=kwargs.get("is_active", True),
                estado_registro=kwargs.get("estado_registro", "Pendiente"),
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Expunge para evitar DetachedInstanceError al salir del context manager
            db.expunge(user)
            
            return user
    
    @staticmethod
    def update_user(user_id: int, **fields) -> Optional[User]:
        """
        Actualiza campos de un usuario.
        
        Args:
            user_id: ID del usuario
            **fields: Campos a actualizar
        
        Returns:
            Usuario actualizado o None si no existe
        """
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Actualizar campos permitidos
            allowed_fields = {
                "nombre", "apellido", "email", "telefono",
                "sector", "posicion", "centros",
                "jefe", "gerente1", "gerente2",
                "is_active", "estado_registro"
            }
            
            for key, value in fields.items():
                if key in allowed_fields and hasattr(user, key):
                    setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            
            # Expunge para evitar DetachedInstanceError
            db.expunge(user)
            
            return user
    
    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """
        Actualiza contraseña de usuario.
        
        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña en texto plano
        
        Returns:
            True si se actualizó, False si usuario no existe
        """
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.password_hash = AuthService.hash_password(new_password)
            db.commit()
            
            return True
