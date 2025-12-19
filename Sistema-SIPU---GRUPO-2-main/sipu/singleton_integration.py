"""Integración del patrón Singleton en el sistema SIPU Flask.

Este módulo integra los singletons de configuración, sesiones y caché
en la aplicación Flask para mejorar el rendimiento y la gestión de estado.
"""

import sys
import os

# Importar singletons desde el módulo de patrones de diseño
patron_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'patron de diseño'))
if patron_path not in sys.path:
    sys.path.insert(0, patron_path)

try:
    from Singleton_SIPU import (
        get_config,
        get_session_manager,
        get_cache_manager,
        SIPUConfiguration,
        SessionManager,
        CacheManager
    )
    SINGLETON_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudo importar Singleton: {e}")
    SINGLETON_AVAILABLE = False


def initialize_singletons():
    """
    Inicializa los singletons del sistema.
    Esta función debe llamarse al inicio de la aplicación.
    """
    if not SINGLETON_AVAILABLE:
        print("⚠️ Sistema Singleton no disponible")
        return False
    
    try:
        # Inicializar configuración
        config = get_config()
        print(f"✅ Configuración inicializada: {config.get('universidad')}")
        
        # Inicializar gestor de sesiones
        session_mgr = get_session_manager()
        print(f"✅ Gestor de sesiones inicializado: {session_mgr}")
        
        # Inicializar gestor de caché
        cache_mgr = get_cache_manager()
        print(f"✅ Gestor de caché inicializado: {cache_mgr}")
        
        return True
    except Exception as e:
        print(f"⚠️ Error al inicializar singletons: {e}")
        return False


def get_app_config(key: str, default=None):
    """
    Obtiene un valor de configuración del singleton.
    
    Args:
        key: Clave de configuración
        default: Valor por defecto si no existe
        
    Returns:
        Valor de configuración o default
    """
    if not SINGLETON_AVAILABLE:
        return default
    
    try:
        config = get_config()
        return config.get(key, default)
    except Exception:
        return default


def cache_periods(periods_list):
    """
    Almacena la lista de períodos en caché.
    
    Args:
        periods_list: Lista de períodos a cachear
    """
    if not SINGLETON_AVAILABLE:
        return
    
    try:
        cache = get_cache_manager()
        cache.set('periods', periods_list, ttl=300)  # 5 minutos
    except Exception as e:
        print(f"⚠️ Error al cachear períodos: {e}")


def get_cached_periods():
    """
    Obtiene la lista de períodos desde caché.
    
    Returns:
        Lista de períodos o None si no está en caché
    """
    if not SINGLETON_AVAILABLE:
        return None
    
    try:
        cache = get_cache_manager()
        return cache.get('periods')
    except Exception:
        return None


def cache_careers(careers_list):
    """
    Almacena la lista de carreras en caché.
    
    Args:
        careers_list: Lista de carreras a cachear
    """
    if not SINGLETON_AVAILABLE:
        return
    
    try:
        cache = get_cache_manager()
        cache.set('careers', careers_list, ttl=300)  # 5 minutos
    except Exception as e:
        print(f"⚠️ Error al cachear carreras: {e}")


def get_cached_careers():
    """
    Obtiene la lista de carreras desde caché.
    
    Returns:
        Lista de carreras o None si no está en caché
    """
    if not SINGLETON_AVAILABLE:
        return None
    
    try:
        cache = get_cache_manager()
        return cache.get('careers')
    except Exception:
        return None


def register_user_session(session_id: str, user_email: str, user_role: str):
    """
    Registra una sesión de usuario activa.
    
    Args:
        session_id: ID único de la sesión
        user_email: Email del usuario
        user_role: Rol del usuario
    """
    if not SINGLETON_AVAILABLE:
        return
    
    try:
        session_mgr = get_session_manager()
        session_mgr.create_session(session_id, user_email, user_role)
    except Exception as e:
        print(f"⚠️ Error al registrar sesión: {e}")


def close_user_session(session_id: str):
    """
    Cierra una sesión de usuario.
    
    Args:
        session_id: ID de la sesión a cerrar
    """
    if not SINGLETON_AVAILABLE:
        return
    
    try:
        session_mgr = get_session_manager()
        session_mgr.close_session(session_id)
    except Exception as e:
        print(f"⚠️ Error al cerrar sesión: {e}")


def get_active_users_count() -> int:
    """
    Obtiene el número de usuarios activos.
    
    Returns:
        Número de usuarios conectados
    """
    if not SINGLETON_AVAILABLE:
        return 0
    
    try:
        session_mgr = get_session_manager()
        return session_mgr.get_active_sessions_count()
    except Exception:
        return 0


def get_system_info() -> dict:
    """
    Obtiene información del sistema usando los singletons.
    
    Returns:
        Diccionario con información del sistema
    """
    if not SINGLETON_AVAILABLE:
        return {
            'singleton_available': False,
            'message': 'Sistema Singleton no disponible'
        }
    
    try:
        config = get_config()
        session_mgr = get_session_manager()
        cache_mgr = get_cache_manager()
        
        return {
            'singleton_available': True,
            'app_name': config.get('app_name'),
            'version': config.get('version'),
            'universidad': config.get('universidad'),
            'sedes': config.get('sedes'),
            'environment': config.get('environment'),
            'active_sessions': session_mgr.get_active_sessions_count(),
            'cache_items': cache_mgr.get_size(),
            'mongodb_enabled': config.get('use_mongodb'),
        }
    except Exception as e:
        return {
            'singleton_available': False,
            'error': str(e)
        }


def clear_all_caches():
    """Limpia todos los cachés del sistema."""
    if not SINGLETON_AVAILABLE:
        return
    
    try:
        cache = get_cache_manager()
        cache.clear()
        print("✅ Caché limpiado correctamente")
    except Exception as e:
        print(f"⚠️ Error al limpiar caché: {e}")
