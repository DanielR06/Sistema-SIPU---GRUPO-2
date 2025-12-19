"""Patrón de Diseño Observer para el Sistema SIPU.

Este módulo implementa el patrón Observer para manejar notificaciones
y eventos del sistema de forma desacoplada. Permite que múltiples observadores
reaccionen a eventos sin que el sujeto (Subject) conozca los detalles de
implementación de cada observador.

Principios de POO aplicados:
- Abstracción: Interfaces Observer y Subject
- Encapsulamiento: Estado interno protegido
- Polimorfismo: Múltiples tipos de observadores
- Inyección de dependencias: Observadores se pasan al sujeto

Casos de uso en SIPU:
- Notificaciones de inscripción de aspirantes
- Alertas de documentos pendientes
- Actualizaciones de estado de períodos
- Logs del sistema

Autor: Mendoza Camas Joan
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json


class EventType(Enum):
    """Tipos de eventos que pueden ser observados en el sistema."""
    STUDENT_REGISTERED = "student_registered"
    STUDENT_UPDATED = "student_updated"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_REJECTED = "document_rejected"
    PERIOD_ACTIVATED = "period_activated"
    PERIOD_DEACTIVATED = "period_deactivated"
    CAREER_ADDED = "career_added"
    CERTIFICATE_GENERATED = "certificate_generated"


class Event:
    """Representa un evento del sistema con sus datos asociados.
    
    Encapsula toda la información relevante de un evento para que
    los observadores puedan procesarla adecuadamente.
    """
    
    def __init__(self, event_type: EventType, data: Dict[str, Any], 
                 source: str = "SIPU_System"):
        """
        Inicializa un evento.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento
            source: Origen del evento
        """
        self._event_type = event_type
        self._data = data
        self._timestamp = datetime.now()
        self._source = source
    
    @property
    def event_type(self) -> EventType:
        """Tipo del evento (solo lectura)."""
        return self._event_type
    
    @property
    def data(self) -> Dict[str, Any]:
        """Datos del evento (solo lectura)."""
        return self._data.copy()  # Retornar copia para inmutabilidad
    
    @property
    def timestamp(self) -> datetime:
        """Timestamp del evento (solo lectura)."""
        return self._timestamp
    
    @property
    def source(self) -> str:
        """Origen del evento (solo lectura)."""
        return self._source
    
    def __str__(self) -> str:
        return f"Event({self.event_type.value}, {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización."""
        return {
            'event_type': self.event_type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }


class Observer(ABC):
    """Interfaz abstracta para observadores.
    
    Los observadores concretos deben implementar el método update()
    para reaccionar a los eventos del sistema.
    """
    
    @abstractmethod
    def update(self, event: Event) -> None:
        """
        Método llamado cuando ocurre un evento.
        
        Args:
            event: Evento que ha ocurrido
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre del observador para identificación."""
        pass


class Subject:
    """Sujeto observable que mantiene y notifica a sus observadores.
    
    Implementa la lógica de registro, eliminación y notificación
    de observadores. Permite filtrado de eventos por tipo.
    """
    
    def __init__(self, name: str = "SIPU_Subject"):
        """
        Inicializa el sujeto observable.
        
        Args:
            name: Nombre identificador del sujeto
        """
        self._name = name
        self._observers: List[Observer] = []
        self._event_history: List[Event] = []
        self._max_history = 100  # Límite de eventos en historial
    
    def attach(self, observer: Observer) -> None:
        """
        Registra un observador para recibir notificaciones.
        
        Args:
            observer: Observador a registrar
        """
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"✅ Observador '{observer.get_name()}' registrado en '{self._name}'")
    
    def detach(self, observer: Observer) -> None:
        """
        Elimina un observador de la lista de notificaciones.
        
        Args:
            observer: Observador a eliminar
        """
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"❌ Observador '{observer.get_name()}' eliminado de '{self._name}'")
    
    def notify(self, event: Event) -> None:
        """
        Notifica a todos los observadores sobre un evento.
        
        Args:
            event: Evento a notificar
        """
        # Agregar al historial
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)  # Eliminar el más antiguo
        
        # Notificar a todos los observadores
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                print(f"⚠️ Error en observador '{observer.get_name()}': {str(e)}")
    
    def get_observers_count(self) -> int:
        """Retorna el número de observadores registrados."""
        return len(self._observers)
    
    def get_event_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """
        Retorna el historial de eventos, opcionalmente filtrado.
        
        Args:
            event_type: Tipo de evento para filtrar (None = todos)
            
        Returns:
            Lista de eventos
        """
        if event_type is None:
            return self._event_history.copy()
        return [e for e in self._event_history if e.event_type == event_type]


# ============================================================================
# OBSERVADORES CONCRETOS
# ============================================================================


class EmailNotificationObserver(Observer):
    """Observador que envía notificaciones por correo electrónico.
    
    En producción, integraría con un servicio SMTP real.
    Esta implementación simula el envío de correos.
    """
    
    def __init__(self, smtp_config: Optional[Dict[str, str]] = None):
        """
        Inicializa el observador de email.
        
        Args:
            smtp_config: Configuración SMTP (servidor, puerto, etc.)
        """
        self._smtp_config = smtp_config or {}
        self._sent_count = 0
    
    def update(self, event: Event) -> None:
        """Procesa el evento y envía notificación por email."""
        # Filtrar eventos relevantes para email
        if event.event_type in [
            EventType.STUDENT_REGISTERED,
            EventType.DOCUMENT_APPROVED,
            EventType.DOCUMENT_REJECTED,
            EventType.CERTIFICATE_GENERATED
        ]:
            self._send_email(event)
    
    def _send_email(self, event: Event) -> None:
        """Simula el envío de un email."""
        recipient = event.data.get('correo', 'unknown@example.com')
        subject = self._get_email_subject(event)
        body = self._get_email_body(event)
        
        # En producción, aquí iría la lógica SMTP real
        print(f"📧 Email enviado a {recipient}")
        print(f"   Asunto: {subject}")
        print(f"   Contenido: {body[:80]}...")
        
        self._sent_count += 1
    
    def _get_email_subject(self, event: Event) -> str:
        """Genera el asunto del email según el tipo de evento."""
        subjects = {
            EventType.STUDENT_REGISTERED: "Inscripción confirmada - SIPU",
            EventType.DOCUMENT_APPROVED: "Documento aprobado - SIPU",
            EventType.DOCUMENT_REJECTED: "Documento requiere revisión - SIPU",
            EventType.CERTIFICATE_GENERATED: "Certificado de inscripción disponible - SIPU"
        }
        return subjects.get(event.event_type, "Notificación - SIPU")
    
    def _get_email_body(self, event: Event) -> str:
        """Genera el cuerpo del email según el tipo de evento."""
        data = event.data
        nombre = data.get('nombre', 'Aspirante')
        
        if event.event_type == EventType.STUDENT_REGISTERED:
            return f"Hola {nombre}, tu inscripción ha sido registrada exitosamente."
        elif event.event_type == EventType.DOCUMENT_APPROVED:
            return f"Hola {nombre}, tu documento ha sido aprobado."
        elif event.event_type == EventType.DOCUMENT_REJECTED:
            return f"Hola {nombre}, tu documento necesita revisión."
        elif event.event_type == EventType.CERTIFICATE_GENERATED:
            return f"Hola {nombre}, tu certificado de inscripción está disponible."
        return "Notificación del sistema SIPU"
    
    def get_name(self) -> str:
        return "EmailNotificationObserver"
    
    def get_sent_count(self) -> int:
        """Retorna el número de emails enviados."""
        return self._sent_count


class LoggingObserver(Observer):
    """Observador que registra todos los eventos en un archivo de log.
    
    Implementa un sistema de logging estructurado para auditoría
    y seguimiento del sistema.
    """
    
    def __init__(self, log_file: str = "sipu_events.log"):
        """
        Inicializa el observador de logging.
        
        Args:
            log_file: Ruta del archivo de log
        """
        self._log_file = log_file
        self._log_count = 0
    
    def update(self, event: Event) -> None:
        """Registra el evento en el archivo de log."""
        log_entry = self._format_log_entry(event)
        
        try:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            self._log_count += 1
            print(f"📝 Evento registrado en {self._log_file}")
        except Exception as e:
            print(f"⚠️ Error al escribir log: {str(e)}")
    
    def _format_log_entry(self, event: Event) -> str:
        """Formatea el evento para el log."""
        timestamp = event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        event_type = event.event_type.value
        data_json = json.dumps(event.data, ensure_ascii=False)
        
        return f"[{timestamp}] {event_type} | {event.source} | {data_json}"
    
    def get_name(self) -> str:
        return "LoggingObserver"
    
    def get_log_count(self) -> int:
        """Retorna el número de eventos registrados."""
        return self._log_count


class StatisticsObserver(Observer):
    """Observador que mantiene estadísticas del sistema.
    
    Recopila métricas y estadísticas para análisis y reporting.
    """
    
    def __init__(self):
        """Inicializa el observador de estadísticas."""
        self._stats: Dict[str, int] = {}
        self._student_count = 0
        self._document_count = 0
    
    def update(self, event: Event) -> None:
        """Actualiza las estadísticas según el evento."""
        event_name = event.event_type.value
        self._stats[event_name] = self._stats.get(event_name, 0) + 1
        
        # Contadores específicos
        if event.event_type == EventType.STUDENT_REGISTERED:
            self._student_count += 1
        elif event.event_type in [EventType.DOCUMENT_UPLOADED, 
                                   EventType.DOCUMENT_APPROVED,
                                   EventType.DOCUMENT_REJECTED]:
            self._document_count += 1
        
        print(f"📊 Estadísticas actualizadas: {event_name} = {self._stats[event_name]}")
    
    def get_name(self) -> str:
        return "StatisticsObserver"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna las estadísticas recopiladas."""
        return {
            'events_by_type': self._stats.copy(),
            'total_students': self._student_count,
            'total_documents': self._document_count,
            'total_events': sum(self._stats.values())
        }
    
    def print_report(self) -> None:
        """Imprime un reporte de estadísticas."""
        print("\n" + "="*60)
        print("REPORTE DE ESTADÍSTICAS - SISTEMA SIPU")
        print("="*60)
        stats = self.get_statistics()
        print(f"Total de eventos: {stats['total_events']}")
        print(f"Total de estudiantes registrados: {stats['total_students']}")
        print(f"Total de documentos procesados: {stats['total_documents']}")
        print("\nEventos por tipo:")
        for event_type, count in stats['events_by_type'].items():
            print(f"  - {event_type}: {count}")
        print("="*60 + "\n")


class DatabaseObserver(Observer):
    """Observador que persiste eventos en la base de datos.
    
    Integra con el repositorio de MongoDB para almacenar
    el historial completo de eventos del sistema.
    """
    
    def __init__(self, repository=None):
        """
        Inicializa el observador de base de datos.
        
        Args:
            repository: Instancia del repositorio (MongoDB o SQLite)
        """
        self._repository = repository
        self._event_count = 0
    
    def update(self, event: Event) -> None:
        """Guarda el evento en la base de datos."""
        if self._repository is None:
            return
        
        # En una implementación real, guardaríamos en una colección de eventos
        # Por ahora, solo incrementamos el contador
        self._event_count += 1
        print(f"💾 Evento guardado en base de datos (Total: {self._event_count})")
    
    def get_name(self) -> str:
        return "DatabaseObserver"
    
    def get_event_count(self) -> int:
        """Retorna el número de eventos guardados."""
        return self._event_count


# ============================================================================
# INTEGRACIÓN CON SIPU
# ============================================================================


class SIPUEventManager:
    """Gestor centralizado de eventos para el sistema SIPU.
    
    Singleton que coordina la emisión de eventos y la gestión
    de observadores en toda la aplicación.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implementa el patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de eventos (solo una vez)."""
        if self._initialized:
            return
        
        self._subject = Subject("SIPU_EventManager")
        self._initialized = True
        print("🎯 SIPU Event Manager inicializado")
    
    def add_observer(self, observer: Observer) -> None:
        """Agrega un observador al sistema."""
        self._subject.attach(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """Remueve un observador del sistema."""
        self._subject.detach(observer)
    
    def emit_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Emite un evento al sistema.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento
        """
        event = Event(event_type, data)
        self._subject.notify(event)
    
    def get_observers_count(self) -> int:
        """Retorna el número de observadores activos."""
        return self._subject.get_observers_count()
    
    def get_event_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Retorna el historial de eventos."""
        return self._subject.get_event_history(event_type)


# ============================================================================
# EJEMPLO DE USO
# ============================================================================


def demo_observer_pattern():
    """Demostración del patrón Observer en SIPU."""
    print("\n" + "="*70)
    print("DEMOSTRACIÓN: Patrón Observer en Sistema SIPU")
    print("="*70 + "\n")
    
    # 1. Crear el gestor de eventos (Singleton)
    event_manager = SIPUEventManager()
    
    # 2. Crear observadores
    email_observer = EmailNotificationObserver()
    log_observer = LoggingObserver("demo_sipu.log")
    stats_observer = StatisticsObserver()
    db_observer = DatabaseObserver()
    
    # 3. Registrar observadores
    event_manager.add_observer(email_observer)
    event_manager.add_observer(log_observer)
    event_manager.add_observer(stats_observer)
    event_manager.add_observer(db_observer)
    
    print(f"\n✅ {event_manager.get_observers_count()} observadores registrados\n")
    
    # 4. Simular eventos del sistema
    print("--- Simulando registro de estudiante ---\n")
    event_manager.emit_event(
        EventType.STUDENT_REGISTERED,
        {
            'nombre': 'Juan Pérez',
            'correo': 'juan.perez@example.com',
            'carrera': 'Ingeniería de Sistemas',
            'periodo': '2025-1'
        }
    )
    
    print("\n--- Simulando aprobación de documento ---\n")
    event_manager.emit_event(
        EventType.DOCUMENT_APPROVED,
        {
            'nombre': 'María García',
            'correo': 'maria.garcia@example.com',
            'documento': 'DNI',
            'fecha': '2025-12-18'
        }
    )
    
    print("\n--- Simulando generación de certificado ---\n")
    event_manager.emit_event(
        EventType.CERTIFICATE_GENERATED,
        {
            'nombre': 'Carlos López',
            'correo': 'carlos.lopez@example.com',
            'certificado_id': 'CERT-2025-001'
        }
    )
    
    # 5. Mostrar estadísticas
    print("\n")
    stats_observer.print_report()
    
    print("="*70)
    print("✅ Demostración completada")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Ejecutar demostración
    demo_observer_pattern()
