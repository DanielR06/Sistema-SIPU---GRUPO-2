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
        return self._correo.split("@")[-1] if "@" in self._correo else ""

    @abstractmethod
    def get_rol(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self._nombre} <{self._correo}> ({self.get_rol()})"


class Administrador(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)

    def get_rol(self) -> str:
        return "admin"


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
        return self.__nota

    @nota.setter
    def nota(self, valor: float):
        if valor is None:
            raise ValueError("La nota no puede ser None")
        if valor < 0 or valor > 20:
            raise ValueError("La nota debe estar en 0..20")
        self.__nota = valor

    def ejecutar_evaluacion(self):
        print("Ejecutando evaluación...")


# Entidades placeholder
class Universidad:
    def __init__(self, nombre_universidad: str, sedes: List[str]):
        self.nombre_universidad = nombre_universidad
        self.sedes = sedes


class Documento:
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


# AuthService and InMemory implementation


class AuthService(ABC):
    @abstractmethod
    def authenticate(self, correo: str, contrasena: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def change_password(self, correo: str, old_password: str, new_password: str) -> bool:
        pass

    @abstractmethod
    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool:
        pass


class InMemoryAuthService(AuthService):
    def __init__(self, usuarios_db: List[Dict[str, str]]):
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
            if any(u.get("correo") == new_correo for u in self._usuarios_db if u is not user):
                return False
            user["correo"] = new_correo
        return True


DEFAULT_DB = [
    {"nombre": "Admin Uno", "correo": "admin1", "contrasena": "123", "rol": "admin"},
    {"nombre": "Daniel", "correo": "daniel", "contrasena": "software1", "rol": "postulante"},
    {"nombre": "Admin Tres", "correo": "admin3", "contrasena": "456", "rol": "admin"},
    {"nombre": "Luis", "correo": "luis", "contrasena": "software2", "rol": "postulante"}
]
