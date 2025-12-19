"""
Patrón Bridge para el Sistema SIPU
===================================

Este módulo implementa el patrón Bridge para separar abstracciones de sus
implementaciones, permitiendo flexibilidad en la gestión de persistencia,
notificaciones y generación de reportes.

Autor: Sistema SIPU - Grupo 2
Fecha: Diciembre 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


# ============================================================================
# IMPLEMENTACIONES DE PERSISTENCIA (Implementation)
# ============================================================================

class PersistenceImplementation(ABC):
    """
    Interfaz de implementación para los sistemas de persistencia.
    Define las operaciones básicas que deben soportar todos los backends.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """Establece conexión con el sistema de persistencia"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Cierra la conexión con el sistema de persistencia"""
        pass
    
    @abstractmethod
    def save(self, collection: str, data: Dict[str, Any]) -> bool:
        """Guarda datos en una colección/tabla"""
        pass
    
    @abstractmethod
    def find_all(self, collection: str) -> List[Dict[str, Any]]:
        """Recupera todos los registros de una colección/tabla"""
        pass
    
    @abstractmethod
    def find_by_id(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Busca un registro por su ID"""
        pass
    
    @abstractmethod
    def delete(self, collection: str, record_id: str) -> bool:
        """Elimina un registro por su ID"""
        pass
    
    @abstractmethod
    def get_info(self) -> str:
        """Retorna información sobre el sistema de persistencia"""
        pass


class MongoDBImplementation(PersistenceImplementation):
    """Implementación concreta usando MongoDB"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017"):
        self.connection_string = connection_string
        self.connected = False
        self.database_name = "sipu_db"
        print(f"🔧 MongoDB Implementation creada: {connection_string}")
    
    def connect(self) -> bool:
        print(f"📡 Conectando a MongoDB: {self.connection_string}")
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        print("🔌 Desconectando de MongoDB")
        self.connected = False
        return True
    
    def save(self, collection: str, data: Dict[str, Any]) -> bool:
        if not self.connected:
            raise ConnectionError("MongoDB no está conectado")
        
        print(f"💾 MongoDB: Guardando en colección '{collection}'")
        print(f"   Datos: {json.dumps(data, indent=2)}")
        return True
    
    def find_all(self, collection: str) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("MongoDB no está conectado")
        
        print(f"🔍 MongoDB: Recuperando todos los documentos de '{collection}'")
        return []
    
    def find_by_id(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("MongoDB no está conectado")
        
        print(f"🔍 MongoDB: Buscando documento con _id='{record_id}' en '{collection}'")
        return None
    
    def delete(self, collection: str, record_id: str) -> bool:
        if not self.connected:
            raise ConnectionError("MongoDB no está conectado")
        
        print(f"🗑️ MongoDB: Eliminando documento con _id='{record_id}' de '{collection}'")
        return True
    
    def get_info(self) -> str:
        return f"MongoDB @ {self.connection_string} (database: {self.database_name})"


class SQLiteImplementation(PersistenceImplementation):
    """Implementación concreta usando SQLite"""
    
    def __init__(self, db_path: str = "sipu.db"):
        self.db_path = db_path
        self.connected = False
        print(f"🔧 SQLite Implementation creada: {db_path}")
    
    def connect(self) -> bool:
        print(f"📡 Conectando a SQLite: {self.db_path}")
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        print("🔌 Desconectando de SQLite")
        self.connected = False
        return True
    
    def save(self, collection: str, data: Dict[str, Any]) -> bool:
        if not self.connected:
            raise ConnectionError("SQLite no está conectado")
        
        # SQLite usa "tables" en lugar de "collections"
        print(f"💾 SQLite: Insertando en tabla '{collection}'")
        print(f"   Datos: {json.dumps(data, indent=2)}")
        return True
    
    def find_all(self, collection: str) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("SQLite no está conectado")
        
        print(f"🔍 SQLite: SELECT * FROM {collection}")
        return []
    
    def find_by_id(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("SQLite no está conectado")
        
        print(f"🔍 SQLite: SELECT * FROM {collection} WHERE id='{record_id}'")
        return None
    
    def delete(self, collection: str, record_id: str) -> bool:
        if not self.connected:
            raise ConnectionError("SQLite no está conectado")
        
        print(f"🗑️ SQLite: DELETE FROM {collection} WHERE id='{record_id}'")
        return True
    
    def get_info(self) -> str:
        return f"SQLite @ {self.db_path}"


class InMemoryImplementation(PersistenceImplementation):
    """Implementación en memoria para testing"""
    
    def __init__(self):
        self.storage: Dict[str, List[Dict[str, Any]]] = {}
        self.connected = False
        print("🔧 InMemory Implementation creada")
    
    def connect(self) -> bool:
        print("📡 Conectando a almacenamiento en memoria")
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        print("🔌 Desconectando almacenamiento en memoria")
        self.connected = False
        return True
    
    def save(self, collection: str, data: Dict[str, Any]) -> bool:
        if not self.connected:
            raise ConnectionError("InMemory storage no está conectado")
        
        if collection not in self.storage:
            self.storage[collection] = []
        
        self.storage[collection].append(data)
        print(f"💾 InMemory: Guardando en '{collection}' (total: {len(self.storage[collection])})")
        return True
    
    def find_all(self, collection: str) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("InMemory storage no está conectado")
        
        records = self.storage.get(collection, [])
        print(f"🔍 InMemory: Recuperando {len(records)} registros de '{collection}'")
        return records
    
    def find_by_id(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("InMemory storage no está conectado")
        
        records = self.storage.get(collection, [])
        for record in records:
            if record.get('id') == record_id:
                print(f"🔍 InMemory: Encontrado registro con id='{record_id}'")
                return record
        
        print(f"🔍 InMemory: No se encontró registro con id='{record_id}'")
        return None
    
    def delete(self, collection: str, record_id: str) -> bool:
        if not self.connected:
            raise ConnectionError("InMemory storage no está conectado")
        
        if collection in self.storage:
            original_count = len(self.storage[collection])
            self.storage[collection] = [r for r in self.storage[collection] if r.get('id') != record_id]
            deleted = original_count - len(self.storage[collection])
            print(f"🗑️ InMemory: Eliminados {deleted} registros con id='{record_id}'")
            return deleted > 0
        
        return False
    
    def get_info(self) -> str:
        total_records = sum(len(records) for records in self.storage.values())
        return f"InMemory Storage (collections: {len(self.storage)}, records: {total_records})"


# ============================================================================
# ABSTRACCIÓN DE REPOSITORIO (Abstraction)
# ============================================================================

class Repository:
    """
    Abstracción que usa una implementación de persistencia.
    Proporciona una interfaz de alto nivel para operaciones de datos.
    """
    
    def __init__(self, implementation: PersistenceImplementation):
        self.implementation = implementation
        print(f"🏗️ Repository creado con: {implementation.get_info()}")
    
    def set_implementation(self, implementation: PersistenceImplementation):
        """Permite cambiar la implementación en tiempo de ejecución"""
        self.implementation = implementation
        print(f"🔄 Repository cambiado a: {implementation.get_info()}")
    
    def initialize(self) -> bool:
        """Inicializa la conexión con el sistema de persistencia"""
        return self.implementation.connect()
    
    def close(self) -> bool:
        """Cierra la conexión con el sistema de persistencia"""
        return self.implementation.disconnect()
    
    def create(self, collection: str, data: Dict[str, Any]) -> bool:
        """Crea un nuevo registro"""
        data['created_at'] = datetime.now().isoformat()
        return self.implementation.save(collection, data)
    
    def read_all(self, collection: str) -> List[Dict[str, Any]]:
        """Lee todos los registros"""
        return self.implementation.find_all(collection)
    
    def read_one(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Lee un registro específico"""
        return self.implementation.find_by_id(collection, record_id)
    
    def remove(self, collection: str, record_id: str) -> bool:
        """Elimina un registro"""
        return self.implementation.delete(collection, record_id)
    
    def get_backend_info(self) -> str:
        """Retorna información sobre el backend actual"""
        return self.implementation.get_info()


# ============================================================================
# REPOSITORIO ESPECIALIZADO PARA ESTUDIANTES (Refined Abstraction)
# ============================================================================

class StudentRepository(Repository):
    """
    Repositorio especializado para gestionar estudiantes.
    Extiende la abstracción base con operaciones específicas del dominio.
    """
    
    COLLECTION_NAME = "students"
    
    def register_student(self, student_data: Dict[str, Any]) -> bool:
        """
        Registra un nuevo estudiante en el sistema.
        
        Args:
            student_data: Datos del estudiante (dni, name, email, career, period)
            
        Returns:
            True si el registro fue exitoso
        """
        print(f"👤 Registrando estudiante: {student_data.get('name')}")
        
        # Agregar metadatos
        student_data['registered_at'] = datetime.now().isoformat()
        student_data['status'] = 'active'
        
        return self.create(self.COLLECTION_NAME, student_data)
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Obtiene todos los estudiantes registrados"""
        print(f"📋 Obteniendo todos los estudiantes")
        return self.read_all(self.COLLECTION_NAME)
    
    def get_student_by_dni(self, dni: str) -> Optional[Dict[str, Any]]:
        """
        Busca un estudiante por su DNI.
        Nota: Esta es una implementación simplificada.
        """
        print(f"🔍 Buscando estudiante con DNI: {dni}")
        students = self.get_all_students()
        for student in students:
            if student.get('dni') == dni:
                return student
        return None
    
    def delete_student(self, student_id: str) -> bool:
        """Elimina un estudiante del sistema"""
        print(f"🗑️ Eliminando estudiante con ID: {student_id}")
        return self.remove(self.COLLECTION_NAME, student_id)


# ============================================================================
# IMPLEMENTACIONES DE NOTIFICACIÓN (Implementation para otro Bridge)
# ============================================================================

class NotificationImplementation(ABC):
    """Interfaz para implementaciones de notificación"""
    
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str) -> bool:
        """Envía una notificación"""
        pass
    
    @abstractmethod
    def get_channel(self) -> str:
        """Retorna el canal de notificación"""
        pass


class EmailNotification(NotificationImplementation):
    """Implementación de notificaciones por email"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com"):
        self.smtp_server = smtp_server
        print(f"📧 Email Notification creada: {smtp_server}")
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        print(f"📧 Enviando email a: {recipient}")
        print(f"   Asunto: {subject}")
        print(f"   Mensaje: {message[:50]}...")
        return True
    
    def get_channel(self) -> str:
        return f"Email (SMTP: {self.smtp_server})"


class SMSNotification(NotificationImplementation):
    """Implementación de notificaciones por SMS"""
    
    def __init__(self, provider: str = "Twilio"):
        self.provider = provider
        print(f"📱 SMS Notification creada: {provider}")
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        # SMS no usa subject
        print(f"📱 Enviando SMS a: {recipient}")
        print(f"   Mensaje: {message[:100]}...")
        return True
    
    def get_channel(self) -> str:
        return f"SMS ({self.provider})"


class PushNotification(NotificationImplementation):
    """Implementación de notificaciones push"""
    
    def __init__(self, service: str = "Firebase"):
        self.service = service
        print(f"🔔 Push Notification creada: {service}")
    
    def send(self, recipient: str, subject: str, message: str) -> bool:
        print(f"🔔 Enviando push notification a: {recipient}")
        print(f"   Título: {subject}")
        print(f"   Mensaje: {message[:50]}...")
        return True
    
    def get_channel(self) -> str:
        return f"Push Notification ({self.service})"


# ============================================================================
# ABSTRACCIÓN DE NOTIFICADOR (Abstraction)
# ============================================================================

class Notifier:
    """
    Abstracción para enviar notificaciones usando diferentes implementaciones.
    """
    
    def __init__(self, implementation: NotificationImplementation):
        self.implementation = implementation
        print(f"🔔 Notifier creado con: {implementation.get_channel()}")
    
    def set_implementation(self, implementation: NotificationImplementation):
        """Cambia la implementación de notificación"""
        self.implementation = implementation
        print(f"🔄 Notifier cambiado a: {implementation.get_channel()}")
    
    def notify(self, recipient: str, subject: str, message: str) -> bool:
        """Envía una notificación"""
        return self.implementation.send(recipient, subject, message)
    
    def get_channel_info(self) -> str:
        """Retorna información sobre el canal de notificación"""
        return self.implementation.get_channel()


class StudentNotifier(Notifier):
    """
    Notificador especializado para estudiantes.
    Proporciona métodos de notificación específicos del dominio.
    """
    
    def notify_registration(self, student: Dict[str, Any]) -> bool:
        """Notifica a un estudiante sobre su inscripción exitosa"""
        recipient = student.get('email', '')
        name = student.get('name', 'Estudiante')
        
        subject = "Inscripción Exitosa - SIPU"
        message = f"""
        Hola {name},
        
        Tu inscripción en el Sistema SIPU ha sido exitosa.
        
        Detalles:
        - DNI: {student.get('dni')}
        - Carrera: {student.get('career')}
        - Periodo: {student.get('period')}
        
        Bienvenido/a!
        """
        
        return self.notify(recipient, subject, message.strip())
    
    def notify_certificate(self, student: Dict[str, Any], certificate_url: str) -> bool:
        """Notifica a un estudiante que su certificado está listo"""
        recipient = student.get('email', '')
        name = student.get('name', 'Estudiante')
        
        subject = "Certificado Generado - SIPU"
        message = f"""
        Hola {name},
        
        Tu certificado ha sido generado exitosamente.
        
        Puedes descargarlo en: {certificate_url}
        """
        
        return self.notify(recipient, subject, message.strip())


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DEMOSTRACIÓN DEL PATRÓN BRIDGE EN SIPU")
    print("=" * 70)
    
    # ========================================================================
    # EJEMPLO 1: Repositorio con diferentes backends
    # ========================================================================
    print("\n1️⃣ REPOSITORIO CON DIFERENTES BACKENDS")
    print("-" * 70)
    
    # Crear repositorio con MongoDB
    print("\n🔹 Usando MongoDB:")
    mongo_impl = MongoDBImplementation("mongodb://localhost:27017")
    student_repo = StudentRepository(mongo_impl)
    student_repo.initialize()
    
    student_data = {
        'id': 'EST001',
        'dni': '1234567890',
        'name': 'Juan Pérez',
        'email': 'juan.perez@uleam.edu.ec',
        'career': 'Ingeniería en Sistemas',
        'period': '2024-1'
    }
    
    student_repo.register_student(student_data)
    student_repo.get_all_students()
    student_repo.close()
    
    # Cambiar a SQLite en tiempo de ejecución
    print("\n🔹 Cambiando a SQLite:")
    sqlite_impl = SQLiteImplementation("sipu.db")
    student_repo.set_implementation(sqlite_impl)
    student_repo.initialize()
    
    student_repo.register_student(student_data)
    student_repo.close()
    
    # Cambiar a InMemory para testing
    print("\n🔹 Cambiando a InMemory (testing):")
    memory_impl = InMemoryImplementation()
    student_repo.set_implementation(memory_impl)
    student_repo.initialize()
    
    student_repo.register_student(student_data)
    
    student_data_2 = {
        'id': 'EST002',
        'dni': '0987654321',
        'name': 'María López',
        'email': 'maria.lopez@uleam.edu.ec',
        'career': 'Medicina',
        'period': '2024-1'
    }
    student_repo.register_student(student_data_2)
    
    all_students = student_repo.get_all_students()
    print(f"   Total estudiantes en memoria: {len(all_students)}")
    
    student_repo.close()
    
    # ========================================================================
    # EJEMPLO 2: Notificaciones con diferentes canales
    # ========================================================================
    print("\n\n2️⃣ NOTIFICACIONES CON DIFERENTES CANALES")
    print("-" * 70)
    
    student = {
        'name': 'Carlos Mendoza',
        'email': 'carlos.mendoza@uleam.edu.ec',
        'dni': '1357924680',
        'career': 'Arquitectura',
        'period': '2024-2'
    }
    
    # Notificar por Email
    print("\n🔹 Notificación por Email:")
    email_impl = EmailNotification()
    notifier = StudentNotifier(email_impl)
    notifier.notify_registration(student)
    
    # Cambiar a SMS
    print("\n🔹 Notificación por SMS:")
    sms_impl = SMSNotification()
    notifier.set_implementation(sms_impl)
    notifier.notify_registration(student)
    
    # Cambiar a Push Notification
    print("\n🔹 Notificación Push:")
    push_impl = PushNotification()
    notifier.set_implementation(push_impl)
    notifier.notify_certificate(student, "https://sipu.uleam.edu.ec/cert/12345")
    
    # ========================================================================
    # EJEMPLO 3: Múltiples notificaciones simultáneas
    # ========================================================================
    print("\n\n3️⃣ MÚLTIPLES CANALES DE NOTIFICACIÓN")
    print("-" * 70)
    
    # Crear notificadores para cada canal
    email_notifier = StudentNotifier(EmailNotification())
    sms_notifier = StudentNotifier(SMSNotification())
    push_notifier = StudentNotifier(PushNotification())
    
    notifiers = [email_notifier, sms_notifier, push_notifier]
    
    print("\n📢 Enviando notificación por todos los canales:")
    for notif in notifiers:
        print(f"   - Canal: {notif.get_channel_info()}")
        notif.notify_registration(student)
        print()
    
    print("\n" + "=" * 70)
    print("✅ Demostración completada")
    print("=" * 70)
    print("\n💡 VENTAJAS DEL PATRÓN BRIDGE:")
    print("   • Desacopla abstracción de implementación")
    print("   • Permite cambiar backend/canal en tiempo de ejecución")
    print("   • Facilita agregar nuevas implementaciones")
    print("   • Mejora la mantenibilidad y extensibilidad")
    print("=" * 70)
