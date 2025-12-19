"""Integración del patrón Observer con el sistema SIPU existente.

Este módulo muestra cómo integrar el patrón Observer con las rutas
y repositorios actuales del sistema para tener notificaciones en tiempo real.
"""

import sys
import os

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sipu.mongo_repository import MongoDBRepository
from sipu.models import InMemoryAuthService, DEFAULT_DB

# Importar el patrón Observer
sys.path.insert(0, os.path.dirname(__file__))
from Observer import (
    SIPUEventManager, EventType,
    EmailNotificationObserver,
    LoggingObserver,
    StatisticsObserver,
    DatabaseObserver
)


def setup_sipu_observers(repository=None) -> SIPUEventManager:
    """
    Configura todos los observadores del sistema SIPU.
    
    Args:
        repository: Instancia del repositorio (opcional)
        
    Returns:
        Gestor de eventos configurado
    """
    print("\n🔧 Configurando observadores del sistema SIPU...")
    
    # Obtener el gestor de eventos (Singleton)
    event_manager = SIPUEventManager()
    
    # Configurar observadores
    email_observer = EmailNotificationObserver()
    log_observer = LoggingObserver("sipu_production.log")
    stats_observer = StatisticsObserver()
    db_observer = DatabaseObserver(repository)
    
    # Registrar observadores
    event_manager.add_observer(email_observer)
    event_manager.add_observer(log_observer)
    event_manager.add_observer(stats_observer)
    event_manager.add_observer(db_observer)
    
    print(f"✅ Sistema configurado con {event_manager.get_observers_count()} observadores\n")
    
    return event_manager


def simulate_student_registration():
    """Simula el flujo completo de registro de un estudiante con observadores."""
    print("\n" + "="*70)
    print("SIMULACIÓN: Registro de Estudiante con Patrón Observer")
    print("="*70 + "\n")
    
    # 1. Configurar sistema con observadores
    try:
        repo = MongoDBRepository()
        print("✅ Conexión a MongoDB exitosa")
    except Exception as e:
        print(f"⚠️ MongoDB no disponible: {e}")
        print("   Continuando con simulación sin base de datos...\n")
        repo = None
    
    event_manager = setup_sipu_observers(repo)
    
    # 2. Datos del estudiante
    student_data = {
        'nombre': 'Ana Martínez Rodríguez',
        'apellidos': 'Martínez Rodríguez',
        'nombres': 'Ana',
        'correo': 'ana.martinez@ejemplo.com',
        'dni': '75432190',
        'career_id': 'career_sistemas',
        'period_id': 'period_2025_1'
    }
    
    print("--- PASO 1: Registro de Aspirante ---\n")
    
    # Emitir evento de registro
    event_manager.emit_event(
        EventType.STUDENT_REGISTERED,
        {
            'nombre': student_data['nombre'],
            'correo': student_data['correo'],
            'dni': student_data['dni'],
            'carrera': 'Ingeniería de Sistemas',
            'periodo': '2025-1',
            'timestamp': '2025-12-18 10:30:00'
        }
    )
    
    print("\n--- PASO 2: Subida de Documentos ---\n")
    
    # Simular subida de documentos
    documentos = ['DNI', 'Certificado de Estudios', 'Foto 3x4']
    for doc in documentos:
        event_manager.emit_event(
            EventType.DOCUMENT_UPLOADED,
            {
                'nombre': student_data['nombre'],
                'correo': student_data['correo'],
                'documento': doc,
                'fecha_subida': '2025-12-18'
            }
        )
    
    print("\n--- PASO 3: Aprobación de Documentos ---\n")
    
    # Simular aprobación
    for doc in documentos[:2]:  # Aprobar solo los primeros 2
        event_manager.emit_event(
            EventType.DOCUMENT_APPROVED,
            {
                'nombre': student_data['nombre'],
                'correo': student_data['correo'],
                'documento': doc,
                'aprobado_por': 'Admin Sistema',
                'fecha_aprobacion': '2025-12-18'
            }
        )
    
    # Rechazar el último
    event_manager.emit_event(
        EventType.DOCUMENT_REJECTED,
        {
            'nombre': student_data['nombre'],
            'correo': student_data['correo'],
            'documento': documentos[2],
            'razon': 'Foto no cumple con las especificaciones',
            'fecha_rechazo': '2025-12-18'
        }
    )
    
    print("\n--- PASO 4: Generación de Certificado ---\n")
    
    # Generar certificado
    event_manager.emit_event(
        EventType.CERTIFICATE_GENERATED,
        {
            'nombre': student_data['nombre'],
            'correo': student_data['correo'],
            'certificado_id': 'CERT-2025-12-001',
            'fecha_generacion': '2025-12-18 11:00:00'
        }
    )
    
    print("\n" + "="*70)
    print("✅ Simulación completada exitosamente")
    print("="*70 + "\n")
    
    # Mostrar estadísticas finales
    for observer in [o for o in event_manager._subject._observers 
                     if o.get_name() == "StatisticsObserver"]:
        observer.print_report()


def demonstrate_observer_benefits():
    """Demuestra los beneficios del patrón Observer."""
    print("\n" + "="*70)
    print("BENEFICIOS DEL PATRÓN OBSERVER EN SIPU")
    print("="*70 + "\n")
    
    benefits = [
        ("1. Desacoplamiento", 
         "Los módulos no necesitan conocer los detalles de notificación"),
        
        ("2. Extensibilidad", 
         "Nuevos observadores se agregan sin modificar código existente"),
        
        ("3. Reusabilidad", 
         "Los observadores pueden ser reutilizados en diferentes contextos"),
        
        ("4. Mantenibilidad", 
         "Cada observador tiene una responsabilidad única y clara"),
        
        ("5. Escalabilidad", 
         "Múltiples observadores pueden reaccionar al mismo evento"),
        
        ("6. Testing", 
         "Observadores pueden ser testeados independientemente")
    ]
    
    for title, description in benefits:
        print(f"✅ {title}")
        print(f"   {description}\n")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        SISTEMA SIPU - DEMOSTRACIÓN PATRÓN OBSERVER                  ║
║        Programación Orientada a Objetos - Grupo 2                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # 1. Mostrar beneficios del patrón
    demonstrate_observer_benefits()
    
    # 2. Ejecutar simulación completa
    simulate_student_registration()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  ✅ Para integrar en producción, importa setup_sipu_observers()     ║
║     en tu archivo sipu/routes.py y llama al event_manager           ║
║     cuando ocurran eventos relevantes.                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
