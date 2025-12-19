"""
Patrón Chain of Responsibility para el Sistema SIPU
===================================================

Este módulo implementa el patrón Chain of Responsibility para validación
de datos de inscripción y procesamiento de solicitudes en el sistema SIPU.

Autor: Sistema SIPU - Grupo 2
Fecha: Diciembre 2025
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import re
from datetime import datetime


# ============================================================================
# HANDLER BASE
# ============================================================================

class ValidationHandler(ABC):
    """
    Clase base abstracta para los manejadores de validación.
    Define la interfaz común para todos los validadores en la cadena.
    """
    
    def __init__(self):
        self._next_handler: Optional['ValidationHandler'] = None
        self.errors: List[str] = []
    
    def set_next(self, handler: 'ValidationHandler') -> 'ValidationHandler':
        """
        Establece el siguiente manejador en la cadena.
        
        Args:
            handler: El siguiente validador a ejecutar
            
        Returns:
            El handler recibido para permitir encadenamiento
        """
        self._next_handler = handler
        return handler
    
    def handle(self, data: Dict[str, Any]) -> bool:
        """
        Procesa la validación y pasa al siguiente handler si existe.
        
        Args:
            data: Diccionario con los datos a validar
            
        Returns:
            True si todas las validaciones pasan, False en caso contrario
        """
        # Validar en este nivel
        is_valid = self.validate(data)
        
        # Si hay siguiente handler, continuar la cadena
        if self._next_handler:
            next_valid = self._next_handler.handle(data)
            return is_valid and next_valid
        
        return is_valid
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Método abstracto que debe implementar cada validador concreto.
        
        Args:
            data: Datos a validar
            
        Returns:
            True si la validación pasa, False en caso contrario
        """
        pass
    
    def get_errors(self) -> List[str]:
        """Retorna la lista de errores acumulados en toda la cadena"""
        errors = self.errors.copy()
        if self._next_handler:
            errors.extend(self._next_handler.get_errors())
        return errors
    
    def clear_errors(self):
        """Limpia los errores de toda la cadena"""
        self.errors.clear()
        if self._next_handler:
            self._next_handler.clear_errors()


# ============================================================================
# VALIDADORES CONCRETOS PARA INSCRIPCIÓN
# ============================================================================

class DNIValidator(ValidationHandler):
    """Valida que el DNI/Cédula tenga el formato correcto"""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        dni = data.get('dni', '').strip()
        
        if not dni:
            self.errors.append("El DNI es obligatorio")
            return False
        
        # Validar que solo contenga dígitos
        if not dni.isdigit():
            self.errors.append("El DNI debe contener solo números")
            return False
        
        # Validar longitud (10 dígitos para Ecuador)
        if len(dni) != 10:
            self.errors.append("El DNI debe tener 10 dígitos")
            return False
        
        return True


class EmailValidator(ValidationHandler):
    """Valida que el correo electrónico tenga formato válido"""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        email = data.get('email', '').strip().lower()
        
        if not email:
            self.errors.append("El correo electrónico es obligatorio")
            return False
        
        # Patrón regex para validar email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            self.errors.append("El formato del correo electrónico no es válido")
            return False
        
        return True


class NameValidator(ValidationHandler):
    """Valida que el nombre sea válido"""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        name = data.get('name', '').strip()
        
        if not name:
            self.errors.append("El nombre es obligatorio")
            return False
        
        if len(name) < 3:
            self.errors.append("El nombre debe tener al menos 3 caracteres")
            return False
        
        # Validar que solo contenga letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', name):
            self.errors.append("El nombre solo debe contener letras y espacios")
            return False
        
        return True


class AcademicDataValidator(ValidationHandler):
    """Valida los datos académicos (carrera y periodo)"""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        career = data.get('career', '').strip()
        period = data.get('period', '').strip()
        
        is_valid = True
        
        if not career:
            self.errors.append("La carrera es obligatoria")
            is_valid = False
        
        if not period:
            self.errors.append("El periodo es obligatorio")
            is_valid = False
        
        return is_valid


class DuplicateValidator(ValidationHandler):
    """Valida que no existan registros duplicados"""
    
    def __init__(self, existing_records: List[Dict[str, Any]]):
        super().__init__()
        self.existing_records = existing_records
    
    def validate(self, data: Dict[str, Any]) -> bool:
        dni = data.get('dni', '').strip()
        email = data.get('email', '').strip().lower()
        
        for record in self.existing_records:
            if record.get('dni') == dni:
                self.errors.append(f"Ya existe un registro con el DNI {dni}")
                return False
            
            if record.get('email', '').lower() == email:
                self.errors.append(f"Ya existe un registro con el correo {email}")
                return False
        
        return True


# ============================================================================
# VALIDADORES PARA AUTENTICACIÓN
# ============================================================================

class CredentialsValidator(ValidationHandler):
    """Valida que las credenciales no estén vacías"""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        is_valid = True
        
        if not username:
            self.errors.append("El nombre de usuario es obligatorio")
            is_valid = False
        
        if not password:
            self.errors.append("La contraseña es obligatoria")
            is_valid = False
        
        return is_valid


class PasswordStrengthValidator(ValidationHandler):
    """Valida la fortaleza de la contraseña"""
    
    def __init__(self, min_length: int = 6):
        super().__init__()
        self.min_length = min_length
    
    def validate(self, data: Dict[str, Any]) -> bool:
        password = data.get('password', '')
        
        if len(password) < self.min_length:
            self.errors.append(f"La contraseña debe tener al menos {self.min_length} caracteres")
            return False
        
        return True


# ============================================================================
# FACTORY PARA CREAR CADENAS DE VALIDACIÓN
# ============================================================================

class ValidationChainFactory:
    """
    Factory para crear cadenas de validación predefinidas según el contexto.
    """
    
    @staticmethod
    def create_registration_chain(existing_records: List[Dict[str, Any]] = None) -> ValidationHandler:
        """
        Crea una cadena de validación para el proceso de inscripción.
        
        Args:
            existing_records: Lista de registros existentes para validar duplicados
            
        Returns:
            El primer handler de la cadena de validación
        """
        # Crear los validadores
        dni_validator = DNIValidator()
        email_validator = EmailValidator()
        name_validator = NameValidator()
        academic_validator = AcademicDataValidator()
        
        # Encadenar los validadores
        dni_validator.set_next(email_validator) \
                     .set_next(name_validator) \
                     .set_next(academic_validator)
        
        # Agregar validador de duplicados si se proporcionan registros
        if existing_records:
            duplicate_validator = DuplicateValidator(existing_records)
            academic_validator.set_next(duplicate_validator)
        
        return dni_validator
    
    @staticmethod
    def create_login_chain(require_strong_password: bool = False) -> ValidationHandler:
        """
        Crea una cadena de validación para el proceso de login.
        
        Args:
            require_strong_password: Si se debe validar fortaleza de contraseña
            
        Returns:
            El primer handler de la cadena de validación
        """
        credentials_validator = CredentialsValidator()
        
        if require_strong_password:
            password_validator = PasswordStrengthValidator(min_length=8)
            credentials_validator.set_next(password_validator)
        
        return credentials_validator


# ============================================================================
# PROCESADORES DE SOLICITUDES (Chain of Responsibility para workflow)
# ============================================================================

class RequestHandler(ABC):
    """
    Handler base para procesar solicitudes en el sistema.
    """
    
    def __init__(self):
        self._next_handler: Optional['RequestHandler'] = None
    
    def set_next(self, handler: 'RequestHandler') -> 'RequestHandler':
        self._next_handler = handler
        return handler
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa la solicitud y la pasa al siguiente handler.
        
        Args:
            request: Diccionario con los datos de la solicitud
            
        Returns:
            Diccionario con el resultado del procesamiento
        """
        result = self.process(request)
        
        # Si el procesamiento fue exitoso y hay siguiente handler, continuar
        if result.get('success', False) and self._next_handler:
            return self._next_handler.handle_request(request)
        
        return result
    
    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa la solicitud en este nivel.
        
        Args:
            request: Datos de la solicitud
            
        Returns:
            Diccionario con el resultado del procesamiento
        """
        pass


class AuthorizationHandler(RequestHandler):
    """Verifica que el usuario tenga permisos para realizar la acción"""
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_role = request.get('user_role', 'guest')
        required_role = request.get('required_role', 'user')
        
        # Jerarquía de roles
        role_hierarchy = {'guest': 0, 'student': 1, 'professor': 2, 'admin': 3}
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level >= required_level:
            return {
                'success': True,
                'message': f'Usuario autorizado con rol: {user_role}',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'message': f'Permisos insuficientes. Se requiere rol: {required_role}',
                'timestamp': datetime.now().isoformat()
            }


class DataValidationHandler(RequestHandler):
    """Valida los datos de la solicitud"""
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = request.get('required_fields', [])
        data = request.get('data', {})
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return {
                'success': False,
                'message': f'Campos faltantes: {", ".join(missing_fields)}',
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'success': True,
            'message': 'Datos validados correctamente',
            'timestamp': datetime.now().isoformat()
        }


class LoggingHandler(RequestHandler):
    """Registra la solicitud en el sistema de logging"""
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get('action', 'unknown')
        user = request.get('user_id', 'anonymous')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'action': action,
            'details': request.get('data', {})
        }
        
        print(f"📝 LOG: {log_entry}")
        
        return {
            'success': True,
            'message': 'Solicitud registrada en log',
            'log_entry': log_entry
        }


class ProcessingHandler(RequestHandler):
    """Procesa la lógica de negocio de la solicitud"""
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get('action', 'unknown')
        data = request.get('data', {})
        
        # Aquí iría la lógica específica de procesamiento
        print(f"⚙️ PROCESANDO: {action} con datos: {data}")
        
        return {
            'success': True,
            'message': f'Acción {action} procesada exitosamente',
            'result': data,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DEMOSTRACIÓN DEL PATRÓN CHAIN OF RESPONSIBILITY EN SIPU")
    print("=" * 70)
    
    # ========================================================================
    # EJEMPLO 1: Validación de datos de inscripción
    # ========================================================================
    print("\n1️⃣ VALIDACIÓN DE DATOS DE INSCRIPCIÓN")
    print("-" * 70)
    
    # Datos válidos
    valid_data = {
        'dni': '1234567890',
        'email': 'juan.perez@uleam.edu.ec',
        'name': 'Juan Pérez García',
        'career': 'Ingeniería en Sistemas',
        'period': '2024-1'
    }
    
    # Crear cadena de validación
    validator = ValidationChainFactory.create_registration_chain()
    
    print("\n✅ Validando datos VÁLIDOS:")
    if validator.handle(valid_data):
        print("   ✓ Todos los datos son válidos")
    else:
        print("   ✗ Errores encontrados:")
        for error in validator.get_errors():
            print(f"     - {error}")
    
    # Limpiar errores
    validator.clear_errors()
    
    # Datos inválidos
    invalid_data = {
        'dni': '123',  # DNI inválido
        'email': 'correo-invalido',  # Email inválido
        'name': 'AB',  # Nombre muy corto
        'career': '',  # Carrera vacía
        'period': ''   # Periodo vacío
    }
    
    print("\n❌ Validando datos INVÁLIDOS:")
    if validator.handle(invalid_data):
        print("   ✓ Todos los datos son válidos")
    else:
        print("   ✗ Errores encontrados:")
        for error in validator.get_errors():
            print(f"     - {error}")
    
    # ========================================================================
    # EJEMPLO 2: Validación con verificación de duplicados
    # ========================================================================
    print("\n\n2️⃣ VALIDACIÓN CON VERIFICACIÓN DE DUPLICADOS")
    print("-" * 70)
    
    existing_students = [
        {'dni': '1234567890', 'email': 'existente@uleam.edu.ec'}
    ]
    
    validator_with_dup = ValidationChainFactory.create_registration_chain(existing_students)
    
    duplicate_data = {
        'dni': '1234567890',  # DNI duplicado
        'email': 'nuevo@uleam.edu.ec',
        'name': 'María López',
        'career': 'Medicina',
        'period': '2024-1'
    }
    
    validator_with_dup.clear_errors()
    print("\n🔍 Validando datos con DNI duplicado:")
    if validator_with_dup.handle(duplicate_data):
        print("   ✓ Datos válidos")
    else:
        print("   ✗ Errores encontrados:")
        for error in validator_with_dup.get_errors():
            print(f"     - {error}")
    
    # ========================================================================
    # EJEMPLO 3: Procesamiento de solicitudes con autorización
    # ========================================================================
    print("\n\n3️⃣ PROCESAMIENTO DE SOLICITUDES CON AUTORIZACIÓN")
    print("-" * 70)
    
    # Crear cadena de procesamiento
    auth_handler = AuthorizationHandler()
    validation_handler = DataValidationHandler()
    logging_handler = LoggingHandler()
    processing_handler = ProcessingHandler()
    
    auth_handler.set_next(validation_handler) \
                .set_next(logging_handler) \
                .set_next(processing_handler)
    
    # Solicitud con permisos suficientes
    request_admin = {
        'user_id': 'admin001',
        'user_role': 'admin',
        'required_role': 'professor',
        'action': 'generate_certificate',
        'required_fields': ['student_id', 'course_id'],
        'data': {
            'student_id': 'EST001',
            'course_id': 'CS101'
        }
    }
    
    print("\n✅ Procesando solicitud con ROL ADMIN:")
    result = auth_handler.handle_request(request_admin)
    print(f"   Resultado: {result['message']}")
    
    # Solicitud sin permisos suficientes
    request_student = {
        'user_id': 'student001',
        'user_role': 'student',
        'required_role': 'admin',
        'action': 'delete_student',
        'required_fields': ['student_id'],
        'data': {'student_id': 'EST002'}
    }
    
    print("\n❌ Procesando solicitud con ROL STUDENT (insuficiente):")
    result = auth_handler.handle_request(request_student)
    print(f"   Resultado: {result['message']}")
    
    print("\n" + "=" * 70)
    print("✅ Demostración completada")
    print("=" * 70)
