"""Paquete de clases del sistema SIPU.

Este paquete contiene todas las clases del dominio organizadas en módulos:
- usuarios: Administrador, Aspirante, Usuario
- evaluacion: Evaluacion
- entidades: Universidad, Documento, Carrera, etc.
- auth: AuthService, InMemoryAuthService

Uso:
    from clases import Administrador, Aspirante, InMemoryAuthService
    from clases.auth import DEFAULT_DB
"""

# Importar todas las clases para acceso directo
from .usuarios import Usuario, Administrador, Aspirante
from .evaluacion import Evaluacion
from .entidades import (
    Universidad, Documento, Notificacion, Reporte, 
    Postulacion, OfertaAcademica, Periodo, Laboratorio,
    Sede, Carrera, Nota
)
from .auth import AuthService, InMemoryAuthService, DEFAULT_DB

# También importar desde sipu.models para compatibilidad
from sipu.models import *  # noqa: F401,F403

# Exportar todas las clases
__all__ = [
    # Usuarios
    'Usuario', 'Administrador', 'Aspirante',
    # Evaluación
    'Evaluacion',
    # Entidades
    'Universidad', 'Documento', 'Notificacion', 'Reporte',
    'Postulacion', 'OfertaAcademica', 'Periodo', 'Laboratorio',
    'Sede', 'Carrera', 'Nota',
    # Autenticación
    'AuthService', 'InMemoryAuthService', 'DEFAULT_DB'
]
