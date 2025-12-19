"""
Integración del patrón Bridge en SIPU
======================================

Este módulo integra el patrón Bridge para gestionar diferentes canales
de notificación (Email, SMS, Push) de manera desacoplada.

Autor: Sistema SIPU - Grupo 2
Fecha: Diciembre 2025
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Importar el patrón Bridge
sys.path.insert(0, str(Path(__file__).parent.parent))
from patrones_diseño.Bridge import (
    EmailNotification,
    SMSNotification,
    PushNotification,
    StudentNotifier,
    NotificationImplementation
)


# ============================================================================
# GESTOR GLOBAL DE NOTIFICACIONES
# ============================================================================

class NotificationManager:
    """
    Gestor centralizado de notificaciones que usa el patrón Bridge.
    Mantiene múltiples notificadores con diferentes implementaciones.
    """
    
    def __init__(self):
        self.notifiers: Dict[str, StudentNotifier] = {}
        self._initialize_notifiers()
    
    def _initialize_notifiers(self):
        """Inicializa los notificadores con sus implementaciones"""
        # Email notifier (canal principal)
        email_impl = EmailNotification(smtp_server="smtp.uleam.edu.ec")
        self.notifiers['email'] = StudentNotifier(email_impl)
        
        # SMS notifier (canal secundario)
        sms_impl = SMSNotification(provider="TwilioEC")
        self.notifiers['sms'] = StudentNotifier(sms_impl)
        
        # Push notifier (canal opcional)
        push_impl = PushNotification(service="Firebase")
        self.notifiers['push'] = StudentNotifier(push_impl)
    
    def notify_registration(self, student: Dict[str, Any], channels: List[str] = None) -> bool:
        """
        Notifica sobre un registro exitoso a través de los canales especificados.
        
        Args:
            student: Datos del estudiante registrado
            channels: Lista de canales a usar ['email', 'sms', 'push']
                     Si es None, usa solo 'email'
        
        Returns:
            True si al menos una notificación fue exitosa
        """
        if channels is None:
            channels = ['email']  # Por defecto solo email
        
        success = False
        for channel in channels:
            notifier = self.notifiers.get(channel)
            if notifier:
                try:
                    if notifier.notify_registration(student):
                        success = True
                        print(f"✅ Notificación enviada por {channel}")
                except Exception as e:
                    print(f"⚠️ Error en notificación {channel}: {e}")
        
        return success
    
    def notify_certificate(self, student: Dict[str, Any], certificate_url: str, channels: List[str] = None) -> bool:
        """
        Notifica sobre un certificado generado.
        
        Args:
            student: Datos del estudiante
            certificate_url: URL o ruta del certificado
            channels: Lista de canales a usar
        
        Returns:
            True si al menos una notificación fue exitosa
        """
        if channels is None:
            channels = ['email']
        
        success = False
        for channel in channels:
            notifier = self.notifiers.get(channel)
            if notifier:
                try:
                    if notifier.notify_certificate(student, certificate_url):
                        success = True
                        print(f"✅ Notificación de certificado enviada por {channel}")
                except Exception as e:
                    print(f"⚠️ Error en notificación {channel}: {e}")
        
        return success
    
    def get_available_channels(self) -> List[str]:
        """Retorna la lista de canales disponibles"""
        return list(self.notifiers.keys())
    
    def add_channel(self, name: str, implementation: NotificationImplementation):
        """
        Agrega un nuevo canal de notificación dinámicamente.
        
        Args:
            name: Nombre del canal
            implementation: Implementación del canal
        """
        self.notifiers[name] = StudentNotifier(implementation)
        print(f"➕ Canal '{name}' agregado: {implementation.get_channel()}")


# Instancia global del gestor de notificaciones
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """
    Retorna la instancia global del gestor de notificaciones.
    Implementa patrón Singleton para el gestor.
    """
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# ============================================================================
# FUNCIONES DE CONVENIENCIA PARA USAR EN ROUTES
# ============================================================================

def notify_student_registration(student_data: dict, use_sms: bool = False) -> bool:
    """
    Notifica a un estudiante sobre su registro exitoso.
    
    Args:
        student_data: Diccionario con datos del estudiante
            - nombre o name: Nombre del estudiante
            - correo o email: Email del estudiante
            - dni: DNI del estudiante
            - career_id o career: Carrera
            - period_id o period: Período
        use_sms: Si se debe enviar también notificación por SMS
    
    Returns:
        True si al menos una notificación fue exitosa
    
    Example:
        >>> student = {
        ...     'nombre': 'Juan Pérez',
        ...     'correo': 'juan@uleam.edu.ec',
        ...     'dni': '1234567890',
        ...     'career_id': 'ING_SISTEMAS',
        ...     'period_id': '2024-1'
        ... }
        >>> notify_student_registration(student, use_sms=True)
    """
    manager = get_notification_manager()
    
    # Normalizar datos del estudiante
    normalized_student = {
        'name': student_data.get('nombre') or student_data.get('name', 'Estudiante'),
        'email': student_data.get('correo') or student_data.get('email', ''),
        'dni': student_data.get('dni', ''),
        'career': student_data.get('career_name') or student_data.get('career_id') or student_data.get('career', 'N/A'),
        'period': student_data.get('period_name') or student_data.get('period_id') or student_data.get('period', 'N/A')
    }
    
    # Determinar canales a usar
    channels = ['email']
    if use_sms:
        channels.append('sms')
    
    return manager.notify_registration(normalized_student, channels)


def notify_certificate_generated(student_data: dict, certificate_path: str = None) -> bool:
    """
    Notifica a un estudiante que su certificado está listo.
    
    Args:
        student_data: Datos del estudiante
        certificate_path: Ruta o URL del certificado
    
    Returns:
        True si la notificación fue exitosa
    
    Example:
        >>> student = {'nombre': 'Juan Pérez', 'correo': 'juan@uleam.edu.ec'}
        >>> notify_certificate_generated(student, '/certificates/12345.pdf')
    """
    manager = get_notification_manager()
    
    # Normalizar datos
    normalized_student = {
        'name': student_data.get('nombre') or student_data.get('name', 'Estudiante'),
        'email': student_data.get('correo') or student_data.get('email', '')
    }
    
    # URL del certificado (simplificado)
    cert_url = certificate_path or "https://sipu.uleam.edu.ec/certificados"
    
    return manager.notify_certificate(normalized_student, cert_url, channels=['email'])


def send_custom_notification(recipient: str, subject: str, message: str, channel: str = 'email') -> bool:
    """
    Envía una notificación personalizada.
    
    Args:
        recipient: Destinatario (email o teléfono)
        subject: Asunto
        message: Mensaje
        channel: Canal a usar ('email', 'sms', 'push')
    
    Returns:
        True si la notificación fue exitosa
    """
    manager = get_notification_manager()
    notifier = manager.notifiers.get(channel)
    
    if notifier:
        try:
            return notifier.notify(recipient, subject, message)
        except Exception as e:
            print(f"⚠️ Error enviando notificación: {e}")
            return False
    
    print(f"⚠️ Canal '{channel}' no disponible")
    return False


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def initialize_bridge():
    """
    Inicializa el sistema Bridge de notificaciones.
    Esta función se llama desde __init__.py al arrancar la aplicación.
    """
    manager = get_notification_manager()
    channels = manager.get_available_channels()
    
    print("🌉 Sistema Bridge inicializado")
    print(f"   ✓ Canales de notificación configurados: {', '.join(channels)}")
    
    # Mostrar información de cada canal
    for channel in channels:
        notifier = manager.notifiers[channel]
        print(f"   • {channel}: {notifier.get_channel_info()}")
    
    return True


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA DE INTEGRACIÓN - BRIDGE PATTERN")
    print("=" * 70)
    
    # Inicializar sistema
    initialize_bridge()
    
    # Simular registro de estudiante
    print("\n📝 Simulando notificación de registro:")
    student = {
        'nombre': 'María López',
        'correo': 'maria.lopez@uleam.edu.ec',
        'dni': '0987654321',
        'career_id': 'Medicina',
        'period_id': '2024-1'
    }
    
    notify_student_registration(student, use_sms=False)
    
    # Simular generación de certificado
    print("\n📄 Simulando notificación de certificado:")
    notify_certificate_generated(student, '/certificates/maria_lopez_2024.pdf')
    
    # Notificación personalizada
    print("\n✉️ Enviando notificación personalizada:")
    send_custom_notification(
        recipient='admin@uleam.edu.ec',
        subject='Nuevo registro en SIPU',
        message='Se ha registrado un nuevo estudiante en el sistema.',
        channel='email'
    )
    
    # Mostrar canales disponibles
    print("\n📡 Canales disponibles:")
    manager = get_notification_manager()
    for channel in manager.get_available_channels():
        print(f"   • {channel}")
    
    print("\n" + "=" * 70)
    print("✅ Integración verificada")
    print("=" * 70)
