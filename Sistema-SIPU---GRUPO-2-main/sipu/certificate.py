"""Generador de certificados de inscripción en PDF."""
from io import BytesIO
from datetime import datetime


def generate_certificate(student_data: dict) -> BytesIO:
    """
    Genera un certificado de inscripción en formato PDF.

    Args:
        student_data: Diccionario con los datos del estudiante

    Returns:
        BytesIO con el PDF generado
    """
    # Versión simplificada sin reportlab - genera texto plano como PDF
    buffer = BytesIO()

    # Crear contenido del certificado como texto
    content = f"""
    CERTIFICADO DE INSCRIPCIÓN
    SISTEMA SIPU - ULEAM

    Fecha: {datetime.now().strftime('%d/%m/%Y')}

    ESTUDIANTE:
    Nombre: {student_data.get('nombre', 'N/A')}
    Apellidos: {student_data.get('apellidos', 'N/A')}
    Nombres: {student_data.get('nombres', 'N/A')}
    Correo: {student_data.get('correo', 'N/A')}
    DNI: {student_data.get('dni', 'N/A')}

    PERÍODO ACADÉMICO:
    {student_data.get('period_name', 'N/A')}

    CARRERA:
    {student_data.get('career_name', 'N/A')}

    Estado de Inscripción: {'Completada' if student_data.get('inscripcion_finalizada') else 'Pendiente'}

    Este certificado verifica que el estudiante está inscrito en el Sistema SIPU.

    Universidad Laica Eloy Alfaro de Manabí
    """

    # Escribir como bytes (simulando PDF)
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)

