from abc import ABC, abstractmethod
from typing import List

# ==========================================
# SECCIÓN: USUARIOS (Unidad 2: Herencia y Polimorfismo)
# ==========================================

class Usuario(ABC):
    """Clase base abstracta (Polimorfismo con clases abstractas)."""
    def __init__(self, nombre: str, correo: str):
        self._nombre = nombre  # Encapsulamiento
        self._correo = correo

    @property
    def nombre(self): return self._nombre

    @property
    def correo(self): return self._correo

    @abstractmethod
    def get_rol(self) -> str:
        """Método abstracto que obliga a las subclases a implementarlo."""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(nombre={self._nombre}, correo={self._correo})"

class Administrador(Usuario):
    def get_rol(self) -> str:
        return "admin"

    def crear_universidad(self, nombre: str, sedes: List[str]):
        # Ya no necesitamos import local porque todo está en este archivo
        return Universidad(nombre, sedes)

class Aspirante(Usuario):
    def __init__(self, nombre, correo, dni=None, periodo=None, carrera=None, jornada=None, sede=None):
        super().__init__(nombre, correo) # Llama al padre Usuario
        self.dni = dni
        self.periodo = periodo
        self.carrera = carrera
        self.jornada = jornada
        self.sede = sede
        self.rol = 'aspirante'
        self.estado = 'Pendiente'

    def get_rol(self) -> str:
        return "postulante"
    
    @property
    def estado(self): return self._estado
    
    @estado.setter
    def estado(self, nuevo_estado):
        self._estado = nuevo_estado

# ==========================================
# SECCIÓN: ENTIDADES (Unidad 1: Encapsulamiento)
# ==========================================

class Universidad:
    def __init__(self, nombre: str, sedes: List[str]):
        self._nombre = nombre
        self._sedes = sedes

    @property
    def nombre(self): return self._nombre

class Documento:
    """Entidad con encapsulamiento total y validación interna."""
    def __init__(self, tipo: str, nombre_archivo: str, propietario: str):
        self._tipo = tipo
        self._nombre_archivo = nombre_archivo
        self._propietario = propietario
        self._estado_aprobacion = "Pendiente"
        self._observaciones = ""

    @property
    def estado_aprobacion(self):
        return self._estado_aprobacion

    def revisar_documento(self, estado: str, observaciones: str):
        """Lógica de negocio encapsulada."""
        validos = ["Aprobado", "Rechazado", "Pendiente"]
        if estado in validos:
            self._estado_aprobacion = estado
            self._observaciones = observaciones
        else:
            raise ValueError(f"Estado no válido. Use: {validos}")

# ==========================================
# SECCIÓN: EVALUACIÓN (Unidad 1: Propiedades)
# ==========================================

class Evaluacion:
    def __init__(self, nota: float, tiempo_evaluacion: int):
        self.__nota = None
        self.nota = nota # Usa el setter para validar desde el inicio
        self._tiempo = tiempo_evaluacion

    @property
    def nota(self) -> float:
        return self.__nota

    @nota.setter
    def nota(self, valor: float):
        if valor < 0 or valor > 20:
            raise ValueError("La nota debe estar entre 0 y 20")
        self.__nota = valor

# ==========================================
# PLACEHOLDERS (Para mantener la estructura)
# ==========================================
class Notificacion: pass
class Reporte: pass
class Postulacion: pass
class OfertaAcademica: pass
class Carrera: pass