"""Módulo de autenticación.

Contiene las interfaces y servicios de autenticación con inyección de dependencias.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from .usuarios import Usuario, Administrador, Aspirante


class AuthService(ABC):
    """Interfaz para un servicio de autenticación.

    Implementaciones concretas (ej. InMemoryAuthService) deben
    respetar este contrato para permitir inyección y bajo acoplamiento.
    """

    @abstractmethod
    def authenticate(self, correo: str, contrasena: str) -> Optional[Usuario]:
        """
        Autentica un usuario.
        
        Args:
            correo: Correo del usuario
            contrasena: Contraseña del usuario
            
        Returns:
            Instancia de Usuario si las credenciales son válidas, None si no
        """
        pass

    @abstractmethod
    def change_password(self, correo: str, old_password: str, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Returns:
            True si se cambió correctamente, False si no
        """
        pass

    @abstractmethod
    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool:
        """
        Actualiza información del usuario (nombre/correo).
        
        Returns:
            True si se actualizó correctamente, False si no
        """
        pass


class InMemoryAuthService(AuthService):
    """Implementación simple en memoria del AuthService.

    Demuestra inyección de dependencias: la base de datos (lista) se
    pasa al constructor en lugar de ser referenciada globalmente.
    """

    def __init__(self, usuarios_db: List[Dict[str, str]]):
        """
        Inicializa el servicio con una base de datos en memoria.
        
        Args:
            usuarios_db: Lista de diccionarios con datos de usuarios
        """
        self._usuarios_db = usuarios_db

    def _find_user_row(self, correo: str) -> Optional[Dict[str, str]]:
        """Encuentra un usuario por correo."""
        for u in self._usuarios_db:
            if u.get("correo") == correo:
                return u
        return None

    def authenticate(self, correo: str, contrasena: str) -> Optional[Usuario]:
        """Autentica un usuario con correo y contraseña."""
        for u in self._usuarios_db:
            if u.get("correo") == correo and u.get("contrasena") == contrasena:
                rol = u.get("rol", "postulante")
                nombre = u.get("nombre", correo)
                # Polimorfismo: devolvemos la subclase adecuada
                if rol == "admin":
                    return Administrador(nombre, correo)
                else:
                    return Aspirante(nombre, correo)
        return None

    def change_password(self, correo: str, old_password: str, new_password: str) -> bool:
        """Cambia la contraseña de un usuario."""
        user = self._find_user_row(correo)
        if not user:
            return False
        if user.get("contrasena") != old_password:
            return False
        user["contrasena"] = new_password
        return True

    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool:
        """Actualiza información del usuario."""
        user = self._find_user_row(correo)
        if not user:
            return False
        if nombre:
            user["nombre"] = nombre
        if new_correo:
            # Evitar colisión de correos
            if any(u.get("correo") == new_correo for u in self._usuarios_db if u is not user):
                return False
            user["correo"] = new_correo
        return True


# Datos de ejemplo (pueden inyectarse en la UI o en tests)
DEFAULT_DB = [
    {"nombre": "Admin Uno", "correo": "admin@sipu.com", "contrasena": "admin123", "rol": "admin"},
    {"nombre": "Daniel", "correo": "daniel@sipu.com", "contrasena": "software1", "rol": "postulante"},
    {"nombre": "Admin Tres", "correo": "admin3@sipu.com", "contrasena": "456", "rol": "admin"},
    {"nombre": "Luis", "correo": "luis@sipu.com", "contrasena": "software2", "rol": "postulante"}
]
