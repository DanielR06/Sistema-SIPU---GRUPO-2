"""Script de prueba para verificar el patrón Singleton en SIPU.

Este script verifica que:
1. Los singletons se inicializan correctamente
2. Solo existe una instancia de cada clase
3. El caché funciona correctamente
4. El gestor de sesiones funciona
"""

import sys
import os

# Agregar el directorio al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("\n" + "="*70)
print("PRUEBA DEL PATRÓN SINGLETON EN EL SISTEMA SIPU")
print("="*70 + "\n")

# 1. Probar importación
print("1️⃣ Verificando disponibilidad del módulo Singleton...")
try:
    from sipu.singleton_integration import (
        initialize_singletons,
        get_app_config,
        cache_periods,
        get_cached_periods,
        register_user_session,
        get_active_users_count,
        get_system_info,
        SINGLETON_AVAILABLE
    )
    
    if not SINGLETON_AVAILABLE:
        print("   ❌ ERROR: El módulo Singleton no está disponible\n")
        sys.exit(1)
    
    print("   ✅ Módulo Singleton disponible\n")
except Exception as e:
    print(f"   ❌ ERROR al importar: {e}\n")
    sys.exit(1)

# 2. Inicializar singletons
print("2️⃣ Inicializando singletons...")
try:
    result = initialize_singletons()
    if not result:
        print("   ❌ ERROR: No se pudieron inicializar los singletons\n")
        sys.exit(1)
    print("   ✅ Singletons inicializados correctamente\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# 3. Verificar que sean verdaderos singletons
print("3️⃣ Verificando que las instancias sean únicas...")
try:
    import sys
    patron_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'patron de diseño'))
    if patron_path not in sys.path:
        sys.path.insert(0, patron_path)
    
    from Singleton_SIPU import (
        get_config,
        get_session_manager,
        get_cache_manager
    )
    
    # Probar configuración
    config1 = get_config()
    config2 = get_config()
    print(f"   Config1: {config1}")
    print(f"   Config2: {config2}")
    print(f"   ¿Son la misma instancia?: {config1 is config2}")
    if config1 is not config2:
        print("   ❌ ERROR: No son la misma instancia\n")
        sys.exit(1)
    
    # Probar gestor de sesiones
    session1 = get_session_manager()
    session2 = get_session_manager()
    print(f"\n   SessionManager1: {session1}")
    print(f"   SessionManager2: {session2}")
    print(f"   ¿Son la misma instancia?: {session1 is session2}")
    if session1 is not session2:
        print("   ❌ ERROR: No son la misma instancia\n")
        sys.exit(1)
    
    # Probar gestor de caché
    cache1 = get_cache_manager()
    cache2 = get_cache_manager()
    print(f"\n   CacheManager1: {cache1}")
    print(f"   CacheManager2: {cache2}")
    print(f"   ¿Son la misma instancia?: {cache1 is cache2}")
    if cache1 is not cache2:
        print("   ❌ ERROR: No son la misma instancia\n")
        sys.exit(1)
    
    print("\n   ✅ Todas las instancias son únicas (Singleton correcto)\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# 4. Probar configuración
print("4️⃣ Probando SIPUConfiguration...")
try:
    app_name = get_app_config('app_name')
    universidad = get_app_config('universidad')
    sedes = get_app_config('sedes', [])
    
    print(f"   Aplicación: {app_name}")
    print(f"   Universidad: {universidad}")
    print(f"   Sedes: {', '.join(sedes)}")
    print("   ✅ Configuración funcionando\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# 5. Probar caché
print("5️⃣ Probando CacheManager...")
try:
    # Cachear períodos
    test_periods = [
        {'id': '1', 'name': '2025-1', 'active': True},
        {'id': '2', 'name': '2025-2', 'active': False}
    ]
    cache_periods(test_periods)
    print("   ✅ Períodos cacheados")
    
    # Recuperar desde caché
    cached = get_cached_periods()
    if cached is None:
        print("   ❌ ERROR: No se pudo recuperar del caché\n")
        sys.exit(1)
    
    print(f"   ✅ Recuperados {len(cached)} períodos desde caché")
    print(f"   Contenido: {cached[0]['name']}, {cached[1]['name']}\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# 6. Probar gestor de sesiones
print("6️⃣ Probando SessionManager...")
try:
    # Registrar sesiones de prueba
    register_user_session("test_session_1", "admin@sipu.com", "admin")
    register_user_session("test_session_2", "user1@sipu.com", "student")
    register_user_session("test_session_3", "user2@sipu.com", "student")
    
    active_count = get_active_users_count()
    print(f"   ✅ Sesiones activas: {active_count}")
    
    if active_count == 0:
        print("   ⚠️ ADVERTENCIA: No hay sesiones activas registradas")
    else:
        print(f"   ✅ Se registraron {active_count} sesiones correctamente\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# 7. Obtener información del sistema
print("7️⃣ Obteniendo información del sistema...")
try:
    system_info = get_system_info()
    if not system_info.get('singleton_available'):
        print("   ❌ ERROR: Singleton no disponible\n")
        sys.exit(1)
    
    print("   ✅ Información del sistema:")
    print(f"      - Aplicación: {system_info.get('app_name')}")
    print(f"      - Versión: {system_info.get('version')}")
    print(f"      - Universidad: {system_info.get('universidad')}")
    print(f"      - Entorno: {system_info.get('environment')}")
    print(f"      - Sesiones activas: {system_info.get('active_sessions', 0)}")
    print(f"      - Items en caché: {system_info.get('cache_items', 0)}")
    print(f"      - MongoDB habilitado: {system_info.get('mongodb_enabled')}\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")
    sys.exit(1)

# 8. Resultado final
print("="*70)
print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("="*70)
print("\nEl patrón Singleton está funcionando correctamente en el sistema SIPU.")
print("Los singletons garantizan una única instancia de:\n")
print("  • 🔧 SIPUConfiguration - Configuración centralizada del sistema")
print("  • 👥 SessionManager - Gestión de sesiones activas")
print("  • 💾 CacheManager - Caché de datos para optimizar rendimiento\n")
print("Beneficios implementados:")
print("  • ✅ Una única fuente de verdad para la configuración")
print("  • ✅ Gestión centralizada de sesiones de usuario")
print("  • ✅ Caché compartido que reduce consultas a la BD")
print("  • ✅ Optimización del uso de memoria\n")
