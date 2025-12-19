"""Patrón de Diseño Singleton aplicado al Sistema SIPU.

Este módulo implementa el patrón Singleton para garantizar que ciertas clases
críticas del sistema tengan una única instancia durante toda la ejecución.

Casos de uso en SIPU:
- Configuración del sistema (una única fuente de verdad)
- Repositorio de datos (conexión única a la base de datos)
- Gestor de sesiones (estado global de usuarios activos)
- Cache del sistema (memoria compartida)

Principios aplicados:
- Single Responsibility: Cada singleton gestiona un aspecto específico
- Lazy Initialization: Las instancias se crean solo cuando se necesitan
- Thread-Safety: Implementación segura para múltiples hilos
"""

from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime
from threading import Lock


class SingletonMeta(type):
    """
    Metaclase para implementar el patrón Singleton de forma thread-safe.
    
    Esta implementación garantiza que:
    - Solo exista una instancia de la clase
    - La creación sea thread-safe (segura para múltiples hilos)
    - Se use lazy initialization (creación bajo demanda)
    """
    
    _instances: Dict[type, Any] = {}
    _lock: Lock = Lock()
    
    def __call__(cls, *args, **kwargs):
        """
        Controla la creación de instancias.
        Usa doble verificación para optimizar el rendimiento.
        """
        # Primera verificación sin lock (optimización de rendimiento)
        if cls not in cls._instances:
            with cls._lock:
                # Segunda verificación con lock (garantía de thread-safety)
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class SIPUConfiguration(metaclass=SingletonMeta):
    """
    Configuración global del sistema SIPU (Singleton).
    
    Centraliza toda la configuración del sistema en una única instancia,
    garantizando consistencia en toda la aplicación.
    """
    
    def __init__(self):
        """Inicializa la configuración solo una vez."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._load_default_config()
        self._load_from_env()
    
    def _load_default_config(self):
        """Carga la configuración por defecto."""
        self._config = {
            'app_name': 'Sistema SIPU',
            'version': '2.0.0',
            'universidad': 'Universidad Laica Eloy Alfaro de Manabí',
            'sedes': ['Manta', 'Chone', 'Bahía de Caráquez', 'Pedernales'],
            'use_mongodb': True,
            'mongodb_uri': 'mongodb://localhost:27017',
            'database_name': 'sipu_db',
            'debug_mode': True,
            'max_file_size_mb': 5,
            'allowed_extensions': ['pdf', 'jpg', 'png', 'jpeg'],
            'session_timeout_minutes': 60,
            'log_level': 'INFO',
            'enable_observers': True,
            'smtp_enabled': False,
            'environment': 'development'
        }
    
    def _load_from_env(self):
        """Sobrescribe con variables de entorno si existen."""
        env_mappings = {
            'USE_MONGODB': ('use_mongodb', lambda x: x.lower() == 'true'),
            'MONGODB_URI': ('mongodb_uri', str),
            'DATABASE_NAME': ('database_name', str),
            'DEBUG': ('debug_mode', lambda x: x.lower() == 'true'),
            'ENVIRONMENT': ('environment', str),
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self._config[config_key] = converter(value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Establece un valor de configuración."""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Retorna toda la configuración como diccionario."""
        return self._config.copy()
    
    def get_universidad_info(self) -> Dict[str, Any]:
        """Retorna información de la universidad."""
        return {
            'nombre': self._config['universidad'],
            'sedes': self._config['sedes'],
            'app': self._config['app_name'],
            'version': self._config['version']
        }
    
    def is_production(self) -> bool:
        """Verifica si está en entorno de producción."""
        return self._config.get('environment', '').lower() == 'production'
    
    def __repr__(self):
        return f"<SIPUConfiguration(env={self._config.get('environment')}, mongodb={self._config.get('use_mongodb')})>"


class SessionManager(metaclass=SingletonMeta):
    """
    Gestor de sesiones activas del sistema (Singleton).
    
    Mantiene un registro de todas las sesiones activas y permite
    gestionar usuarios conectados, timeout, y auditoría.
    """
    
    def __init__(self):
        """Inicializa el gestor de sesiones solo una vez."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._session_history: List[Dict[str, Any]] = []
    
    def create_session(self, session_id: str, user_email: str, user_role: str):
        """Crea una nueva sesión activa."""
        session_data = {
            'session_id': session_id,
            'user_email': user_email,
            'user_role': user_role,
            'login_time': datetime.now(),
            'last_activity': datetime.now(),
            'ip_address': None,
            'user_agent': None
        }
        self._active_sessions[session_id] = session_data
        self._session_history.append({
            'event': 'login',
            'session_id': session_id,
            'user': user_email,
            'timestamp': datetime.now()
        })
    
    def update_activity(self, session_id: str):
        """Actualiza el tiempo de última actividad de una sesión."""
        if session_id in self._active_sessions:
            self._active_sessions[session_id]['last_activity'] = datetime.now()
    
    def close_session(self, session_id: str):
        """Cierra una sesión activa."""
        if session_id in self._active_sessions:
            session_data = self._active_sessions.pop(session_id)
            self._session_history.append({
                'event': 'logout',
                'session_id': session_id,
                'user': session_data['user_email'],
                'timestamp': datetime.now()
            })
    
    def get_active_sessions_count(self) -> int:
        """Retorna el número de sesiones activas."""
        return len(self._active_sessions)
    
    def get_active_users(self) -> List[str]:
        """Retorna lista de usuarios activos."""
        return [s['user_email'] for s in self._active_sessions.values()]
    
    def is_user_online(self, user_email: str) -> bool:
        """Verifica si un usuario está conectado."""
        return any(s['user_email'] == user_email for s in self._active_sessions.values())
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una sesión específica."""
        return self._active_sessions.get(session_id)
    
    def __repr__(self):
        return f"<SessionManager(active={self.get_active_sessions_count()})>"


class CacheManager(metaclass=SingletonMeta):
    """
    Gestor de caché del sistema (Singleton).
    
    Mantiene datos en memoria para acceso rápido y reducir
    consultas a la base de datos.
    """
    
    def __init__(self):
        """Inicializa el gestor de caché solo una vez."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._default_ttl = 300  # 5 minutos por defecto
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Almacena un valor en caché con tiempo de vida."""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de caché si no ha expirado."""
        if key not in self._cache:
            return default
        
        # Verificar si ha expirado
        timestamp = self._cache_timestamps.get(key)
        if timestamp:
            age_seconds = (datetime.now() - timestamp).total_seconds()
            if age_seconds > self._default_ttl:
                self.delete(key)
                return default
        
        return self._cache.get(key, default)
    
    def delete(self, key: str):
        """Elimina un valor de caché."""
        self._cache.pop(key, None)
        self._cache_timestamps.pop(key, None)
    
    def clear(self):
        """Limpia todo el caché."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def get_size(self) -> int:
        """Retorna el número de elementos en caché."""
        return len(self._cache)
    
    def __repr__(self):
        return f"<CacheManager(items={self.get_size()})>"


# Funciones de acceso global a los singletons
def get_config() -> SIPUConfiguration:
    """Obtiene la instancia única de configuración."""
    return SIPUConfiguration()


def get_session_manager() -> SessionManager:
    """Obtiene la instancia única del gestor de sesiones."""
    return SessionManager()


def get_cache_manager() -> CacheManager:
    """Obtiene la instancia única del gestor de caché."""
    return CacheManager()


# Demostración y pruebas
if __name__ == "__main__":
    print("\n" + "="*70)
    print("DEMOSTRACIÓN DEL PATRÓN SINGLETON EN SISTEMA SIPU")
    print("="*70 + "\n")
    
    # 1. Probar SIPUConfiguration
    print("1️⃣ Probando SIPUConfiguration (Singleton)...")
    config1 = get_config()
    config2 = SIPUConfiguration()
    
    print(f"   config1: {config1}")
    print(f"   config2: {config2}")
    print(f"   ¿Son la misma instancia?: {config1 is config2}")
    print(f"   Universidad: {config1.get('universidad')}")
    print(f"   Sedes: {', '.join(config1.get('sedes', []))}")
    
    # Modificar en una instancia
    config1.set('test_value', 'Hola desde config1')
    print(f"   Valor en config2: {config2.get('test_value')}")
    print()
    
    # 2. Probar SessionManager
    print("2️⃣ Probando SessionManager (Singleton)...")
    session_mgr1 = get_session_manager()
    session_mgr2 = SessionManager()
    
    print(f"   session_mgr1: {session_mgr1}")
    print(f"   session_mgr2: {session_mgr2}")
    print(f"   ¿Son la misma instancia?: {session_mgr1 is session_mgr2}")
    
    # Crear sesiones
    session_mgr1.create_session("sess001", "admin@sipu.com", "admin")
    session_mgr1.create_session("sess002", "user@sipu.com", "student")
    
    print(f"   Sesiones activas: {session_mgr2.get_active_sessions_count()}")
    print(f"   Usuarios online: {', '.join(session_mgr2.get_active_users())}")
    print()
    
    # 3. Probar CacheManager
    print("3️⃣ Probando CacheManager (Singleton)...")
    cache1 = get_cache_manager()
    cache2 = CacheManager()
    
    print(f"   cache1: {cache1}")
    print(f"   cache2: {cache2}")
    print(f"   ¿Son la misma instancia?: {cache1 is cache2}")
    
    # Almacenar datos
    cache1.set('periods', [{'id': 1, 'name': '2025-1'}])
    cache1.set('careers_count', 8)
    
    print(f"   Items en cache2: {cache2.get_size()}")
    print(f"   Períodos desde cache2: {cache2.get('periods')}")
    print(f"   Carreras desde cache2: {cache2.get('careers_count')}")
    print()
    
    print("="*70)
    print("✅ SINGLETON FUNCIONANDO CORRECTAMENTE")
    print("="*70)
    print("\nTodas las instancias apuntan al mismo objeto en memoria.")
    print("El patrón Singleton garantiza una única fuente de verdad.\n")
