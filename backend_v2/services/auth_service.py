"""
Backend v2.0 - Authentication service
Lógica de autenticación de usuarios
"""
from __future__ import annotations

from typing import Optional


class AuthService:
    """
    Servicio de autenticación.
    
    TODO FASE 4: Conectar con base de datos real.
    Por ahora usa usuarios hardcodeados para testing.
    """
    
    # Usuarios de prueba (FASE 3 stub)
    STUB_USERS = [
        {
            "id": "admin001",
            "email": "admin@spm.com",
            "password": "admin123",  # TODO: Hash con bcrypt
            "role": "admin"
        },
        {
            "id": "planner001",
            "email": "planificador@spm.com",
            "password": "plan123",
            "role": "planificador"
        },
        {
            "id": "user001",
            "email": "usuario@spm.com",
            "password": "user123",
            "role": "usuario"
        }
    ]
    
    def authenticate_user(
        self, 
        username: str, 
        password: str
    ) -> Optional[dict]:
        """
        Autentica un usuario verificando credenciales.
        
        Args:
            username: Email del usuario
            password: Contraseña en texto plano (TODO: debe llegar hasheada)
        
        Returns:
            Diccionario con datos del usuario si credenciales válidas,
            None si credenciales inválidas.
        
        TODO FASE 4:
            - Consultar usuarios de base de datos
            - Verificar password con bcrypt.verify()
            - Validar que usuario esté activo (estado_registro)
        """
        # Buscar usuario por email
        user = next(
            (u for u in self.STUB_USERS if u["email"].lower() == username.lower()),
            None
        )
        
        if not user:
            return None
        
        # Verificar password (TODO: usar bcrypt)
        if user["password"] != password:
            return None
        
        # Retornar datos del usuario (sin password)
        return {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """
        Obtiene usuario por ID.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Diccionario con datos del usuario o None
        
        TODO FASE 4: Consultar base de datos
        """
        user = next(
            (u for u in self.STUB_USERS if u["id"] == user_id),
            None
        )
        
        if not user:
            return None
        
        return {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
