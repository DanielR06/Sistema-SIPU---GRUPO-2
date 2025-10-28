"""Refactor de clases para demostrar POO avanzada:

Incluye:
- Clases abstractas (ABC)
- Interfaces (AuthService)
- Herencia y polimorfismo (Usuario -> Administrador/Aspirante)
- Inyección de dependencias (AuthService inyectado)
- Decoradores @property
- Diseño acoplado de forma débil (GUI o servicios usan interfaces)

Este archivo contiene las definiciones de dominio y un servicio de
autenticación en memoria que puede inyectarse en una GUI.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict


class Usuario(ABC):
    """Clase base abstracta para usuarios del sistema."""
    def __init__(self, nombre: str, correo: str):
        self._nombre = nombre
        self._correo = correo

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def dominio_correo(self) -> str:
        """Ejemplo de abstracción: propiedad derivada (decorador)."""
        return self._correo.split("@")[-1] if "@" in self._correo else ""

    @abstractmethod
    def get_rol(self) -> str:
        """Cada subclase debe indicar su rol (polimorfismo)."""
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self._nombre} <{self._correo}> ({self.get_rol()})"


class Administrador(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)

    def get_rol(self) -> str:
        return "admin"

    # Ejemplo de método propio (puede crearse una Universidad)
    def crear_universidad(self, nombre_universidad: str, sedes: List[str]):
        return Universidad(nombre_universidad, sedes)


class Aspirante(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)
        self._estado = None

    def definir_estado(self, estado: str):
        self._estado = estado

    def get_rol(self) -> str:
        return "postulante"


class Evaluacion:
    def __init__(self, nota: float, tiempo_evaluacion: int):
        self.__nota = nota
        self.tiempo_evaluacion = tiempo_evaluacion

    @property
    def nota(self) -> float:
        """Getter con encapsulamiento (decorador @property)."""
        return self.__nota

    @nota.setter
    def nota(self, valor: float):
        """Setter que valida y muestra una traza (ejemplo)."""
        if valor is None:
            raise ValueError("La nota no puede ser None")
        if valor < 0 or valor > 20:
            raise ValueError("La nota debe estar en 0..20")
        self.__nota = valor

    def ejecutar_evaluacion(self):
        print("Ejecutando evaluación...")


# Entidades simples/placeholder
class Universidad:
    def __init__(self, nombre_universidad: str, sedes: List[str]):
        self.nombre_universidad = nombre_universidad
        self.sedes = sedes


class Documento:
     def __init__(self, tipodeDocumento, NombreArchivo, FechaSubida, Propietario):
        self.tipodeDocumento=tipodeDocumento
        self.NombreArchivo=NombreArchivo
        self.FechaSubida=FechaSubida
        self.Propietario=Propietario
        self.EstadoAprobacion="Pendiente"
        self.observaciones=""
    def RevisiondeDocumento(self, estado, observaciones):
        self.EstadoAprobacion=estado
        self.observaciones=observaciones
        print(f"El documento ha sido '{self.NombreArchivo} con las siguientes observaciones: {estado} - {observaciones}'")
    def MostrarResumen(self):
        print(f"Documento: {self.NombreArchivo}")
        print(f"Tipo: {self.tipodeDocumento}")
        print(f"Fecha subida: {self.FechaSubida}")
        print(f"Estado: {self.EstadoAprobacion}")
        if self.observaciones:
            print(f"Observaciones: {self.observaciones}")
    pass


class Notificacion:
    pass


class Reporte:
    pass


class Postulacion:
    pass


class OfertaAcademica:
    pass


class Periodo:
    pass


class Laboratorio:
    pass


class Sede:
    pass


class Carrera:
    pass


class Nota:
    pass


# -------------------------------
# Interfaces / Inyección de dependencias
# -------------------------------


class AuthService(ABC):
    """Interfaz para un servicio de autenticación.

    Implementaciones concretas (ej. InMemoryAuthService) deben
    respetar este contrato para permitir inyección y bajo acoplamiento.
    """

    @abstractmethod
    def authenticate(self, correo: str, contrasena: str) -> Optional[Usuario]:
        """Si credenciales válidas, devuelve una instancia de Usuario; si no, None."""

    @abstractmethod
    def change_password(self, correo: str, old_password: str, new_password: str) -> bool:
        """Cambiar la contraseña de un usuario. Devuelve True si se cambió."""

    @abstractmethod
    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool:
        """Actualizar datos del usuario (nombre/correo). Devuelve True si se actualizó."""


class InMemoryAuthService(AuthService):
    """Implementación simple en memoria del AuthService.

    Demonstrates dependency injection: la base de datos (lista) se
    pasa al constructor en lugar de ser referenciada globalmente.
    """

    def __init__(self, usuarios_db: List[Dict[str, str]]):
        # Almacenamos la referencia (inyección) — permite tests y cambio fácil
        self._usuarios_db = usuarios_db

    def _find_user_row(self, correo: str) -> Optional[Dict[str, str]]:
        for u in self._usuarios_db:
            if u.get("correo") == correo:
                return u
        return None

    def authenticate(self, correo: str, contrasena: str) -> Optional[Usuario]:
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
        user = self._find_user_row(correo)
        if not user:
            return False
        if user.get("contrasena") != old_password:
            return False
        user["contrasena"] = new_password
        return True

    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool:
        user = self._find_user_row(correo)
        if not user:
            return False
        if nombre:
            user["nombre"] = nombre
        if new_correo:
            # evitar colisión de correos
            if any(u.get("correo") == new_correo for u in self._usuarios_db if u is not user):
                return False
            user["correo"] = new_correo
        return True


# Datos de ejemplo (pueden inyectarse en la UI o en tests)
DEFAULT_DB = [
    {"nombre": "Admin Uno", "correo": "admin1", "contrasena": "123", "rol": "admin"},
    {"nombre": "Daniel", "correo": "daniel", "contrasena": "software1", "rol": "postulante"},
    {"nombre": "Admin Tres", "correo": "admin3", "contrasena": "456", "rol": "admin"},
    {"nombre": "Luis", "correo": "luis", "contrasena": "software2", "rol": "postulante"}
]


if __name__ == "__main__":
    # Ejemplo de uso en consola (no la interfaz GUI)
    auth = InMemoryAuthService(DEFAULT_DB)
    print("Prueba rápida de autenticación (consola):")
    usuario = auth.authenticate("admin1", "123")
    if usuario:
        print("Autenticado:", usuario)
    else:
        print("Credenciales inválidas")

            

