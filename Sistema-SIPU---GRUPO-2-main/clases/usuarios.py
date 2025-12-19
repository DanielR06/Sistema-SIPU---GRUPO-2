"""Módulo de usuarios del sistema.

Contiene las clases de usuarios (Administrador, Aspirante) con herencia de Usuario.
"""
from abc import ABC, abstractmethod
from typing import List


class Usuario(ABC):
    """Clase base abstracta para usuarios del sistema."""
    
    def __init__(self, nombre: str, correo: str):
        self.nombre = nombre
        self.correo = correo

    @abstractmethod
    def get_rol(self) -> str:
        """Devuelve el rol del usuario."""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(nombre={self.nombre}, correo={self.correo})"


class Administrador(Usuario):
    """Clase para usuarios administradores del sistema."""
    
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)

    def get_rol(self) -> str:
        return "admin"

    def crear_universidad(self, nombre_universidad: str, sedes: List[str]):
        """Crea una instancia de Universidad."""
        from .entidades import Universidad
        return Universidad(nombre_universidad, sedes)


class Aspirante(Usuario):
    """Clase para aspirantes/postulantes al sistema."""
    
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)
        self._estado = None

    def definir_estado(self, estado: str):
        """Define el estado del aspirante."""
        self._estado = estado

    def get_estado(self) -> str:
        """Obtiene el estado actual del aspirante."""
        return self._estado

    def get_rol(self) -> str:
        return "postulante"
