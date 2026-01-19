from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Aspirante, Documento, Universidad

class ISipuRepository(ABC):
    """
    Interfaz para el repositorio principal (Polimorfismo con Clases Abstractas).
    Define las operaciones que cualquier base de datos debe cumplir.
    """

    @abstractmethod
    def guardar_aspirante(self, aspirante: Aspirante) -> bool:
        """Guarda o actualiza un aspirante en el sistema."""
        pass

    @abstractmethod
    def obtener_aspirante_por_correo(self, correo: str) -> Optional[Aspirante]:
        """Busca un aspirante por su correo electrónico."""
        pass

    @abstractmethod
    def listar_documentos(self, propietario_id: str) -> List[Documento]:
        """Obtiene la lista de documentos de un aspirante."""
        pass

class INotificador(ABC):
    """
    Interfaz para el patrón Observer o servicios de mensajería.
    """
    @abstractmethod
    def enviar(self, destinatario: str, mensaje: str):
        pass