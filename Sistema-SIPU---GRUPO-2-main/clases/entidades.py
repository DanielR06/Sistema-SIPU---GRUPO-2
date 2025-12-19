"""Módulo de entidades del dominio.

Contiene clases de entidades como Universidad, Documento, Carrera, etc.
"""
from typing import List


class Universidad:
    """Representa una universidad con sus sedes."""
    
    def __init__(self, nombre_universidad: str, sedes: List[str]):
        self.nombre_universidad = nombre_universidad
        self.sedes = sedes

    def __str__(self):
        return f"Universidad(nombre={self.nombre_universidad}, sedes={len(self.sedes)})"


class Documento:
    """Representa un documento subido por un aspirante."""
    
    def __init__(self, tipodeDocumento: str, NombreArchivo: str, FechaSubida: str, Propietario: str):
        self.tipodeDocumento = tipodeDocumento
        self.NombreArchivo = NombreArchivo
        self.FechaSubida = FechaSubida
        self.Propietario = Propietario
        self.EstadoAprobacion = "Pendiente"
        self.observaciones = ""

    def RevisiondeDocumento(self, estado: str, observaciones: str):
        """Revisa el documento y actualiza su estado."""
        self.EstadoAprobacion = estado
        self.observaciones = observaciones
        print(f"El documento '{self.NombreArchivo}' ha sido revisado: {estado} - {observaciones}")

    def MostrarResumen(self):
        """Muestra un resumen del documento."""
        print(f"Documento: {self.NombreArchivo}")
        print(f"Tipo: {self.tipodeDocumento}")
        print(f"Fecha subida: {self.FechaSubida}")
        print(f"Estado: {self.EstadoAprobacion}")
        if self.observaciones:
            print(f"Observaciones: {self.observaciones}")


class Notificacion:
    """Placeholder para notificaciones del sistema."""
    pass


class Reporte:
    """Placeholder para reportes del sistema."""
    pass


class Postulacion:
    """Placeholder para postulaciones de aspirantes."""
    pass


class OfertaAcademica:
    """Placeholder para ofertas académicas."""
    pass


class Periodo:
    """Placeholder para períodos académicos."""
    pass


class Laboratorio:
    """Placeholder para laboratorios."""
    pass


class Sede:
    """Placeholder para sedes universitarias."""
    pass


class Carrera:
    """Placeholder para carreras universitarias."""
    pass


class Nota:
    """Placeholder para notas académicas."""
    pass
