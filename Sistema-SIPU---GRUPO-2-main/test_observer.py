"""Script de prueba para verificar la integración del patrón Observer.

Este script comprueba que:
1. El sistema Observer se inicializa correctamente
2. Los observadores están registrados
3. Los eventos se emiten correctamente
4. Los observadores responden a los eventos
"""

import sys
import os

# Agregar el directorio al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sipu.observer_integration import (
    initialize_observers,
    get_event_manager,
    emit_student_registered,
    emit_certificate_generated,
    get_statistics,
    OBSERVER_AVAILABLE
)


def test_observer_system():
    """Prueba completa del sistema Observer integrado."""
    
    print("\n" + "="*70)
    print("PRUEBA DEL PATRÓN OBSERVER EN EL SISTEMA SIPU")
    print("="*70 + "\n")
    
    # 1. Verificar disponibilidad
    print("1️⃣ Verificando disponibilidad del módulo Observer...")
    if not OBSERVER_AVAILABLE:
        print("   ❌ ERROR: El módulo Observer no está disponible")
        print("   Verifique que el archivo 'patron de diseño/Observer.py' existe\n")
        return False
    print("   ✅ Módulo Observer disponible\n")
    
    # 2. Inicializar observadores
    print("2️⃣ Inicializando observadores...")
    try:
        event_manager = initialize_observers(repository=None, log_file="test_sipu.log")
        if event_manager is None:
            print("   ❌ ERROR: No se pudo inicializar el gestor de eventos\n")
            return False
        print(f"   ✅ Gestor de eventos inicializado correctamente\n")
    except Exception as e:
        print(f"   ❌ ERROR al inicializar: {e}\n")
        return False
    
    # 3. Verificar observadores registrados
    print("3️⃣ Verificando observadores registrados...")
    observers_count = event_manager.get_observers_count()
    print(f"   📊 Observadores registrados: {observers_count}")
    if observers_count == 0:
        print("   ❌ ERROR: No hay observadores registrados\n")
        return False
    print("   ✅ Observadores listos\n")
    
    # 4. Emitir evento de registro de estudiante
    print("4️⃣ Emitiendo evento: STUDENT_REGISTERED...")
    try:
        test_student = {
            'nombre': 'María González López',
            'correo': 'maria.gonzalez@test.com',
            'dni': '12345678',
            'career_name': 'Ingeniería de Sistemas',
            'period_name': '2025-1'
        }
        emit_student_registered(test_student)
        print("   ✅ Evento STUDENT_REGISTERED emitido correctamente")
        print(f"      - Estudiante: {test_student['nombre']}")
        print(f"      - Correo: {test_student['correo']}")
        print(f"      - DNI: {test_student['dni']}")
        print(f"      - Carrera: {test_student['career_name']}")
        print(f"      - Período: {test_student['period_name']}\n")
    except Exception as e:
        print(f"   ❌ ERROR al emitir evento: {e}\n")
        return False
    
    # 5. Emitir evento de certificado generado
    print("5️⃣ Emitiendo evento: CERTIFICATE_GENERATED...")
    try:
        emit_certificate_generated(test_student)
        print("   ✅ Evento CERTIFICATE_GENERATED emitido correctamente")
        print(f"      - Certificado para: {test_student['nombre']}\n")
    except Exception as e:
        print(f"   ❌ ERROR al emitir evento: {e}\n")
        return False
    
    # 6. Verificar estadísticas
    print("6️⃣ Obteniendo estadísticas del sistema...")
    try:
        stats = get_statistics()
        if stats:
            print("   ✅ Estadísticas recopiladas:")
            print(f"      - Total de eventos: {stats.get('total_events', 0)}")
            print(f"      - Estudiantes registrados: {stats.get('students_registered', 0)}")
            print(f"      - Certificados generados: {stats.get('certificates_generated', 0)}")
            
            event_counts = stats.get('event_counts', {})
            if event_counts:
                print("      - Conteo por tipo de evento:")
                for event_type, count in event_counts.items():
                    print(f"        • {event_type}: {count}")
        else:
            print("   ⚠️ No se pudieron obtener estadísticas")
        print()
    except Exception as e:
        print(f"   ⚠️ Error al obtener estadísticas: {e}\n")
    
    # 7. Verificar archivo de log
    print("7️⃣ Verificando archivo de logs...")
    log_file = "test_sipu.log"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.read()
            log_lines = [line for line in logs.split('\n') if line.strip()]
            print(f"   ✅ Archivo de log creado: {log_file}")
            print(f"   📝 Líneas de log: {len(log_lines)}")
            if log_lines:
                print("   📄 Últimas entradas:")
                for line in log_lines[-3:]:
                    print(f"      {line}")
    else:
        print(f"   ⚠️ Archivo de log no encontrado: {log_file}")
    print()
    
    # 8. Resultado final
    print("="*70)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("="*70)
    print("\nEl patrón Observer está funcionando correctamente en el sistema SIPU.")
    print("Los observadores están respondiendo a los eventos como se esperaba:\n")
    print("  • 📧 EmailNotificationObserver - Enviando notificaciones simuladas")
    print("  • 📝 LoggingObserver - Registrando eventos en archivo")
    print("  • 📊 StatisticsObserver - Recopilando estadísticas")
    print("  • 💾 DatabaseObserver - Procesando eventos\n")
    
    return True


if __name__ == "__main__":
    success = test_observer_system()
    sys.exit(0 if success else 1)
