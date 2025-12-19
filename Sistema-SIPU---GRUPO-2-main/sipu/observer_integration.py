"""Integración del patrón Observer en el sistema SIPU.

Este módulo configura y gestiona los observadores para el sistema,
permitiendo que diferentes componentes reaccionen a eventos del sistema.
"""

import sys
import os

# Importar el patrón Observer desde el directorio padre
patron_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'patrones_diseño'))
if patron_path not in sys.path:
    sys.path.insert(0, patron_path)

try:
    from Observer import (
        SIPUEventManager,
        EventType,
        EmailNotificationObserver,
        LoggingObserver,
        StatisticsObserver,
        DatabaseObserver
    )
    OBSERVER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudo importar el módulo Observer: {e}")
    OBSERVER_AVAILABLE = False
    SIPUEventManager = None
    EventType = None


# Instancia global del gestor de eventos (Singleton)
_event_manager = None


def get_event_manager():
    """Obtiene la instancia del gestor de eventos (Singleton)."""
    global _event_manager
    if _event_manager is None and OBSERVER_AVAILABLE:
        _event_manager = SIPUEventManager()
    return _event_manager


def initialize_observers(repository=None, log_file="sipu_app.log"):
    """
    Inicializa todos los observadores del sistema.
    
    Args:
        repository: Instancia del repositorio para DatabaseObserver
        log_file: Ruta del archivo de logs
        
    Returns:
        SIPUEventManager configurado o None si no está disponible
    """
    if not OBSERVER_AVAILABLE:
        print("⚠️ Sistema Observer no disponible")
        return None
    
    event_manager = get_event_manager()
    
    # Verificar si ya hay observadores registrados
    if event_manager.get_observers_count() > 0:
        return event_manager
    
    try:
        # Configurar observadores
        email_observer = EmailNotificationObserver()
        log_observer = LoggingObserver(log_file)
        stats_observer = StatisticsObserver()
        db_observer = DatabaseObserver(repository)
        
        # Registrar observadores
        event_manager.add_observer(email_observer)
        event_manager.add_observer(log_observer)
        event_manager.add_observer(stats_observer)
        event_manager.add_observer(db_observer)
        
        print(f"✅ Sistema Observer configurado con {event_manager.get_observers_count()} observadores")
        
    except Exception as e:
        print(f"⚠️ Error al configurar observadores: {e}")
    
    return event_manager


def emit_student_registered(student_data):
    """
    Emite un evento de registro de estudiante.
    
    Args:
        student_data: Diccionario con los datos del estudiante
    """
    event_manager = get_event_manager()
    if event_manager and OBSERVER_AVAILABLE:
        try:
            event_manager.emit_event(
                EventType.STUDENT_REGISTERED,
                {
                    'nombre': student_data.get('nombre', ''),
                    'correo': student_data.get('correo', ''),
                    'dni': student_data.get('dni', ''),
                    'carrera': student_data.get('career_name', 'N/A'),
                    'periodo': student_data.get('period_name', 'N/A'),
                }
            )
        except Exception as e:
            print(f"⚠️ Error al emitir evento STUDENT_REGISTERED: {e}")


def emit_certificate_generated(student_data):
    """
    Emite un evento de generación de certificado.
    
    Args:
        student_data: Diccionario con los datos del estudiante
    """
    event_manager = get_event_manager()
    if event_manager and OBSERVER_AVAILABLE:
        try:
            event_manager.emit_event(
                EventType.CERTIFICATE_GENERATED,
                {
                    'nombre': student_data.get('nombre', ''),
                    'correo': student_data.get('correo', ''),
                    'dni': student_data.get('dni', ''),
                    'carrera': student_data.get('career_name', 'N/A'),
                    'periodo': student_data.get('period_name', 'N/A'),
                }
            )
        except Exception as e:
            print(f"⚠️ Error al emitir evento CERTIFICATE_GENERATED: {e}")


def get_statistics():
    """
    Obtiene las estadísticas del sistema desde el observador de estadísticas.
    
    Returns:
        dict: Estadísticas del sistema o None si no está disponible
    """
    event_manager = get_event_manager()
    if not event_manager:
        return None
    
    # Buscar el observador de estadísticas usando el método público
    try:
        # El SIPUEventManager tiene métodos públicos para acceder a observers
        if hasattr(event_manager, 'get_observers_count'):
            # Intentar obtener estadísticas del observador de estadísticas
            # En producción, se necesitaría un método público en el EventManager
            pass
    except Exception as e:
        print(f"⚠️ Error al obtener estadísticas: {e}")
    
    return None


def get_event_history(event_type=None):
    """
    Obtiene el historial de eventos.
    
    Args:
        event_type: Tipo de evento a filtrar (opcional)
        
    Returns:
        list: Lista de eventos
    """
    event_manager = get_event_manager()
    if not event_manager:
        return []
    
    try:
        return event_manager.get_event_history(event_type)
    except Exception as e:
        print(f"⚠️ Error al obtener historial de eventos: {e}")
        return []
