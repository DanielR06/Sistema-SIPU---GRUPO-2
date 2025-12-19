"""Generador de certificados de inscripción en PDF."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo del título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo del subtítulo
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo del cuerpo
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    # Construir el documento
    story = []
    
    # Espaciado superior
    story.append(Spacer(1, 0.5 * inch))
    
    # Encabezado
    story.append(Paragraph("SISTEMA DE INSCRIPCIÓN Y POSTULACIÓN UNIVERSITARIA", title_style))
    story.append(Paragraph("SIPU", subtitle_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Línea decorativa
    line_table = Table([['']], colWidths=[6*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#0066cc')),
    ]))
    story.append(line_table)
    
    story.append(Spacer(1, 0.5 * inch))
    
    # Título del certificado
    story.append(Paragraph("<b>CONSTANCIA DE INSCRIPCIÓN</b>", subtitle_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Texto principal
    story.append(Paragraph(
        "Por medio de la presente se hace constar que:",
        body_style
    ))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Datos del estudiante en tabla con diseño mejorado
    student_info = [
        ['Apellidos y Nombres:', student_data.get('nombre', 'N/A')],
        ['Documento de Identidad:', student_data.get('dni', 'N/A')],
        ['Correo Electrónico:', student_data.get('correo', 'N/A')],
        ['Carrera:', student_data.get('career_name', 'N/A')],
        ['Período Académico:', student_data.get('period_name', 'N/A')],
        ['Código de Inscripción:', str(student_data.get('id', 'N/A'))],
    ]
    
    data_table = Table(student_info, colWidths=[2.8*inch, 3.5*inch], rowHeights=[0.35*inch]*6)
    data_table.setStyle(TableStyle([
        # Fondo degradado alternado para mejor legibilidad
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),  # Azul oscuro para labels
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ffffff')),  # Blanco para valores
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),  # Texto blanco en labels
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e3a5f')),  # Texto azul oscuro en valores
        # Alineación
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Fuentes
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        # Padding para mejor espaciado
        ('LEFTPADDING', (0, 0), (0, -1), 12),
        ('RIGHTPADDING', (0, 0), (0, -1), 12),
        ('LEFTPADDING', (1, 0), (1, -1), 15),
        ('RIGHTPADDING', (1, 0), (1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        # Bordes elegantes
        ('BOX', (0, 0), (-1, -1), 2.5, colors.HexColor('#1e3a5f')),
        ('LINEBELOW', (0, 0), (-1, -2), 1, colors.HexColor('#e0e0e0')),  # Líneas entre filas
        # Sombra sutil (simulada con borde doble)
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
    ]))
    
    story.append(data_table)
    
    story.append(Spacer(1, 0.5 * inch))
    
    # Texto de confirmación
    story.append(Paragraph(
        "Se encuentra <b>INSCRITO(A)</b> como aspirante en el Sistema de "
        "Inscripción y Postulación Universitaria (SIPU).",
        body_style
    ))
    
    story.append(Spacer(1, 0.5 * inch))
    
    # Fecha de emisión
    fecha_emision = datetime.now().strftime("%d de %B de %Y")
    story.append(Paragraph(
        f"<i>Documento emitido el {fecha_emision}</i>",
        body_style
    ))
    
    story.append(Spacer(1, 0.8 * inch))
    
    # Línea de firma
    firma_table = Table([['_' * 50]], colWidths=[4*inch])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(firma_table)
    
    story.append(Spacer(1, 0.1 * inch))
    
    story.append(Paragraph("<b>Oficina de Admisión</b>", body_style))
    story.append(Paragraph("Sistema SIPU", body_style))
    
    # Pie de página
    story.append(Spacer(1, 0.5 * inch))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(
        "Este documento es válido para verificar la inscripción del aspirante.<br/>"
        f"Código único de verificación: {student_data.get('id', 'N/A')}",
        footer_style
    ))
    
    # Construir el PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer
