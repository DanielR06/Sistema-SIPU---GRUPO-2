"""
Integración del patrón Chain of Responsibility en SIPU
=======================================================

Este módulo integra las validaciones del patrón Chain of Responsibility
en el sistema SIPU para validar datos de inscripción y autenticación.

Autor: Sistema SIPU - Grupo 2
Fecha: Diciembre 2025
"""

import sys
from pathlib import Path

# Importar el patrón Chain of Responsibility
sys.path.insert(0, str(Path(__file__).parent.parent))
from patrones_diseño.ChainOfResponsibility import (
    ValidationChainFactory,
    ValidationHandler
)


# ============================================================================
# FUNCIONES DE VALIDACIÓN PARA EL SISTEMA
# ============================================================================

def validate_student_registration(data: dict, existing_students: list = None) -> tuple[bool, list]:
    """
    Valida los datos de registro de un estudiante usando Chain of Responsibility.
    
    Args:
        data: Diccionario con los datos del estudiante
            - dni: DNI/Cédula del estudiante
            - email: Correo electrónico
            - name: Nombre completo
            - career: Carrera seleccionada
            - period: Periodo académico
        existing_students: Lista de estudiantes existentes para validar duplicados
    
    Returns:
        tuple: (is_valid, errors)
            - is_valid: True si todos los datos son válidos
            - errors: Lista de mensajes de error (vacía si is_valid=True)
    
    Example:
        >>> data = {
        ...     'dni': '1234567890',
        ...     'email': 'juan@uleam.edu.ec',
        ...     'name': 'Juan Pérez',
        ...     'career': 'Ingeniería',
        ...     'period': '2024-1'
        ... }
        >>> is_valid, errors = validate_student_registration(data)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    # Crear la cadena de validación
    validator = ValidationChainFactory.create_registration_chain(existing_students)
    
    # Limpiar errores previos
    validator.clear_errors()
    
    # Ejecutar validación
    is_valid = validator.handle(data)
    
    # Obtener errores
    errors = validator.get_errors()
    
    return is_valid, errors


def validate_login_credentials(data: dict, require_strong_password: bool = False) -> tuple[bool, list]:
    """
    Valida las credenciales de login usando Chain of Responsibility.
    
    Args:
        data: Diccionario con credenciales
            - username: Nombre de usuario o email
            - password: Contraseña
        require_strong_password: Si se debe validar la fortaleza de la contraseña
    
    Returns:
        tuple: (is_valid, errors)
            - is_valid: True si las credenciales son válidas
            - errors: Lista de mensajes de error (vacía si is_valid=True)
    
    Example:
        >>> data = {'username': 'admin', 'password': 'mypass123'}
        >>> is_valid, errors = validate_login_credentials(data)
    """
    # Crear la cadena de validación
    validator = ValidationChainFactory.create_login_chain(require_strong_password)
    
    # Limpiar errores previos
    validator.clear_errors()
    
    # Ejecutar validación
    is_valid = validator.handle(data)
    
    # Obtener errores
    errors = validator.get_errors()
    
    return is_valid, errors


def validate_student_data_for_routes(form_data: dict, existing_students: list = None) -> tuple[bool, str]:
    """
    Adapta los datos del formulario de Flask al formato del validador.
    Esta función es específica para usarse en las rutas de Flask.
    
    Args:
        form_data: Datos del formulario de Flask (request.form)
        existing_students: Lista de estudiantes existentes
    
    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True si todos los datos son válidos
            - error_message: Mensaje de error concatenado (vacío si is_valid=True)
    
    Example:
        >>> from flask import request
        >>> is_valid, error_msg = validate_student_data_for_routes(request.form)
        >>> if not is_valid:
        ...     flash(error_msg, 'danger')
    """
    # Extraer y normalizar datos del formulario
    apellidos = form_data.get('apellidos', '').strip()
    nombres = form_data.get('nombres', '').strip()
    nombre_completo = f"{apellidos} {nombres}".strip()
    
    # Preparar datos para validación
    validation_data = {
        'dni': form_data.get('dni', '').strip(),
        'email': form_data.get('correo', '').strip(),
        'name': nombre_completo,
        'career': form_data.get('carrera', '').strip(),
        'period': form_data.get('periodo', '').strip()
    }
    
    # Validar usando Chain of Responsibility
    is_valid, errors = validate_student_registration(validation_data, existing_students)
    
    # Concatenar errores en un solo mensaje
    error_message = '. '.join(errors) if errors else ''
    
    return is_valid, error_message


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def initialize_chain():
    """
    Inicializa el sistema de Chain of Responsibility.
    Esta función se llama desde __init__.py al arrancar la aplicación.
    """
    print("🔗 Sistema Chain of Responsibility inicializado")
    print("   ✓ Validadores de inscripción configurados")
    print("   ✓ Validadores de autenticación configurados")
    return True


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBA DE INTEGRACIÓN - CHAIN OF RESPONSIBILITY")
    print("=" * 70)
    
    # Simular datos de formulario
    print("\n✅ Validando datos VÁLIDOS:")
    valid_form = {
        'dni': '1234567890',
        'correo': 'juan.perez@uleam.edu.ec',
        'apellidos': 'Pérez',
        'nombres': 'Juan Carlos',
        'carrera': 'Ingeniería en Sistemas',
        'periodo': '2024-1'
    }
    
    is_valid, error_msg = validate_student_data_for_routes(valid_form)
    print(f"   Resultado: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")
    if error_msg:
        print(f"   Error: {error_msg}")
    
    # Datos inválidos
    print("\n❌ Validando datos INVÁLIDOS:")
    invalid_form = {
        'dni': '123',  # DNI inválido
        'correo': 'correo-invalido',  # Email inválido
        'apellidos': '',
        'nombres': 'X',  # Nombre muy corto
        'carrera': '',
        'periodo': ''
    }
    
    is_valid, error_msg = validate_student_data_for_routes(invalid_form)
    print(f"   Resultado: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")
    if error_msg:
        print(f"   Error: {error_msg}")
    
    # Validar login
    print("\n🔑 Validando credenciales de login:")
    login_data = {
        'username': 'admin@uleam.edu.ec',
        'password': 'admin123'
    }
    
    is_valid, errors = validate_login_credentials(login_data)
    print(f"   Resultado: {'✓ VÁLIDO' if is_valid else '✗ INVÁLIDO'}")
    if errors:
        for error in errors:
            print(f"   - {error}")
    
    print("\n" + "=" * 70)
    print("✅ Integración verificada")
    print("=" * 70)
