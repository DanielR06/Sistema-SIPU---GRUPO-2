from abc import ABC, abstractmethod
from typing import List, Dict, Optional

"""
Wrapper compatible hacia `sipu.models`.
Integra la lógica de validación (Chain of Responsibility) y gestión de usuarios.
"""

class Usuario:
    def __init__(self, nombre: str, correo: str):
        self.nombre = nombre
        self.correo = correo

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

# ---------------------------------------------------------
# ENTIDADES PRINCIPALES
# ---------------------------------------------------------

class Administrador(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)

    def get_rol(self) -> str:
        return "admin"

    def crear_universidad(self, nombre_universidad: str, sedes: List[str]):
        return Universidad(nombre_universidad, sedes)


class Aspirante(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)
        self._estado = "Pendiente"
        self.puntaje = 0
        self.documentos: List['Documento'] = []

    def definir_estado(self, estado: str):
        self._estado = estado

    def get_rol(self) -> str:
        return "postulante"

    def agregar_documento(self, documento: 'Documento'):
        self.documentos.append(documento)

    def tiene_documento(self, tipo: str) -> bool:
        """Verifica si el aspirante tiene un documento específico aprobado."""
        return any(doc.tipodeDocumento == tipo and doc.EstadoAprobacion == "Aprobado" for doc in self.documentos)


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


class Universidad:
    def __init__(self, nombre_universidad: str, sedes: List[str]):
        self.nombre_universidad = nombre_universidad
        self.sedes = sedes


class Documento:
    def __init__(self, tipodeDocumento, NombreArchivo, FechaSubida, Propietario):
        self.tipodeDocumento = tipodeDocumento
        self.NombreArchivo = NombreArchivo
        self.FechaSubida = FechaSubida
        self.Propietario = Propietario
        self.EstadoAprobacion = "Pendiente"
        self.observaciones = ""

    def RevisiondeDocumento(self, estado, observaciones):
        self.EstadoAprobacion = estado
        self.observaciones = observaciones
        print(f"Resultado de revisión '{self.NombreArchivo}': {estado} - {observaciones}")

    def MostrarResumen(self):
        print(f"Documento: {self.NombreArchivo} | Tipo: {self.tipodeDocumento} | Estado: {self.EstadoAprobacion}")


# --- Clases Placeholder (Se mantienen para compatibilidad) ---
class Notificacion: pass
class Reporte: pass
class Postulacion: pass
class OfertaAcademica: pass
class Periodo: pass
class Laboratorio: pass
class Sede: pass
class Carrera: pass
class Nota: pass


# ---------------------------------------------------------
# CADENA DE RESPONSABILIDAD (PATRÓN DE DISEÑO)
# ---------------------------------------------------------



class Validador(ABC):
    def __init__(self, siguiente=None):
        self.siguiente = siguiente

    @abstractmethod
    def manejar(self, aspirante: Aspirante) -> str:
        if self.siguiente:
            return self.siguiente.manejar(aspirante)
        return "Validación completa: El aspirante cumple con todos los requisitos."


class ValidadorCedula(Validador):
    def manejar(self, aspirante: Aspirante):
        if not aspirante.tiene_documento("Cedula"):
            return "Error: Falta Cédula de Identidad aprobada."
        print("[Validación] Cédula verificada con éxito.")
        return super().manejar(aspirante)


class ValidadorTitulo(Validador):
    def manejar(self, aspirante: Aspirante):
        if not aspirante.tiene_documento("Titulo Bachiller"):
            return "Error: El aspirante no cuenta con Título de Bachiller aprobado."
        print("[Validación] Título de bachiller verificado.")
        return super().manejar(aspirante)


class ValidadorPuntaje(Validador):
    def manejar(self, aspirante: Aspirante):
        # El puntaje mínimo requerido es 600
        if aspirante.puntaje < 600:
            return f"Error: Puntaje {aspirante.puntaje} es insuficiente (Mínimo 600)."
        print(f"[Validación] Puntaje de {aspirante.puntaje} aceptado.")
        return super().manejar(aspirante)


# ---------------------------------------------------------
# SERVICIOS DE AUTENTICACIÓN
# ---------------------------------------------------------

class AuthService(ABC):
    @abstractmethod
    def authenticate(self, correo: str, contrasena: str) -> Optional[Usuario]: pass

    @abstractmethod
    def change_password(self, correo: str, old_password: str, new_password: str) -> bool: pass

    @abstractmethod
    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool: pass


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
        if user and user.get("contrasena") == old_password:
            user["contrasena"] = new_password
            return True
        return False

    def update_user_info(self, correo: str, nombre: Optional[str] = None, new_correo: Optional[str] = None) -> bool:
        user = self._find_user_row(correo)
        if not user: return False
        if nombre: user["nombre"] = nombre
        if new_correo:
            if any(u.get("correo") == new_correo for u in self._usuarios_db if u is not user):
                return False
            user["correo"] = new_correo
        return True


# ---------------------------------------------------------
# DATOS DE PRUEBA Y EJECUCIÓN
# ---------------------------------------------------------

DEFAULT_DB = [
    {"nombre": "Admin Uno", "correo": "admin1", "contrasena": "123", "rol": "admin"},
    {"nombre": "Daniel", "correo": "daniel", "contrasena": "software1", "rol": "postulante"}
]

if __name__ == "__main__":
    auth = InMemoryAuthService(DEFAULT_DB)
    print("--- Sistema de Gestión Académica ---")
    
    # 1. Autenticación
    user = auth.authenticate("daniel", "software1")
    
    if isinstance(user, Aspirante):
        print(f"Bienvenido Postulante: {user.nombre}")
        
        # 2. Configuración de datos del Aspirante
        user.puntaje = 710
        
        # Subir documentos y simular aprobación
        doc_ced = Documento("Cedula", "id_daniel.jpg", "2025-12-18", user.nombre)
        doc_ced.RevisiondeDocumento("Aprobado", "Legible")
        
        doc_tit = Documento("Titulo Bachiller", "bachiller.pdf", "2025-12-18", user.nombre)
        doc_tit.RevisiondeDocumento("Aprobado", "Verificado por el Ministerio")
        
        user.agregar_documento(doc_ced)
        user.agregar_documento(doc_tit)

        # 3. Construcción de la cadena de validación
        # Flujo: Puntaje -> Título -> Cédula
        cadena_validacion = ValidadorPuntaje(ValidadorTitulo(ValidadorCedula()))

        # 4. Ejecución del proceso
        print("\n--- Iniciando Proceso de Validación ---")
        resultado = cadena_validacion.manejar(user)
        print("-" * 40)
        print(f"RESULTADO: {resultado}")