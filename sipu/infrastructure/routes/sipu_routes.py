from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from ...application.services import SipuService
from ..repositories import MongoSipuRepository

# Inicializamos el repositorio y el servicio (Unidad 2: Inyección de Dependencias)
# En un entorno profesional, esto se haría en un 'App Factory'
repo = MongoSipuRepository()
sipu_service = SipuService(repo)

bp = Blueprint('main', __name__)

@bp.route('/aspirante/pdf/<dni>')
def descargar_pdf(dni):
    """Acción de infraestructura para servir el archivo PDF."""
    from flask import send_file
    import io

    # Pedimos al servicio que genere el archivo por DNI
    pdf_buffer = sipu_service.generar_reporte_pdf_por_dni(dni)
    
    if not pdf_buffer:
        flash("No se pudo generar el PDF", "danger")
        return redirect(url_for('main.lista_aspirantes'))

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"reporte_{dni}.pdf",
        mimetype='application/pdf'
    )

@bp.route('/aspirante/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    # Obtener información del usuario en sesión
    correo_usuario = session.get('user_email')
    if not correo_usuario:
        flash('Sesión inválida', 'danger')
        return redirect(url_for('auth.login'))
    
    # Verificar si ya completó inscripción
    aspirante_actual = repo.students.find_one({'correo': correo_usuario})
    if aspirante_actual and aspirante_actual.get('estado') == 'Inscrito':
        flash('Ya has completado tu inscripción', 'info')
        return redirect(url_for('main.aspirante_dashboard'))

    if request.method == 'POST':
        # El servicio procesa los datos del formulario y devuelve el resultado
        exito, mensaje = sipu_service.procesar_inscripcion(request.form)
        
        if exito:
            flash(mensaje, 'success')
            # Después de guardar exitosamente, redirigimos
            return redirect(url_for('main.aspirante_dashboard'), code=303)
        else:
            flash(mensaje, 'danger')
            # Si hay error, mostramos el formulario nuevamente
            periods = list(repo.db.periods.find()) 
            careers = list(repo.db.careers.find())
            sedes = list(repo.db.sedes.find())
            return render_template('inscripcion.html', periods=periods, careers=careers, sedes=sedes)

    # GET: Mostrar el formulario
    # Obtener catálogos para el formulario
    periods = list(repo.db.periods.find()) 
    careers = list(repo.db.careers.find())
    sedes = list(repo.db.sedes.find())
    
    return render_template('inscripcion.html', periods=periods, careers=careers, sedes=sedes)

@bp.route('/aspirante/list')
def lista_aspirantes():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    
    # El servicio devuelve objetos de dominio, no crudos de Mongo
    students = sipu_service.obtener_lista_aspirantes()
    return render_template('lista.html', students=students)

# refactorizacion/sipu/infrastructure/routes/sipu_routes.py

# ... (tus otros imports y el Blueprint bp = Blueprint('main', __name__))

@bp.route('/dashboard')
def dashboard():
    """Ruta del panel principal después del login."""
    from flask import session, render_template, redirect, url_for
    
    # Verificación de seguridad básica (Encapsulamiento de sesión)
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Redirigir según rol
    rol = session.get('rol')
    if rol == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.aspirante_dashboard'))

@bp.route('/admin/dashboard')
def admin_dashboard():
    """Dashboard del administrador."""
    if 'user' not in session or session.get('rol') != 'admin':
        return redirect(url_for('auth.login'))
    
    students = sipu_service.obtener_lista_aspirantes()
    return render_template('admin_dashboard.html', user=session.get('user'), students=students)

@bp.route('/admin/crear-aspirante', methods=['GET', 'POST'])
def crear_aspirante():
    """Admin crea un nuevo aspirante con email y contraseña."""
    if 'user' not in session or session.get('rol') != 'admin':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        
        if not nombre or not correo or not contrasena:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('main.crear_aspirante'))
        
        # Verificar que no exista
        if repo.students.find_one({'correo': correo}):
            flash('El correo ya está registrado', 'danger')
            return redirect(url_for('main.crear_aspirante'))
        
        # Crear aspirante vacío (sin período, carrera, jornada, sede)
        nuevo_aspirante = {
            'nombre': nombre,
            'correo': correo,
            'contrasena': contrasena,
            'rol': 'aspirante',
            'estado': 'Incompleto',  # Estado diferente
            'dni': None,
            'periodo': None,
            'carrera': None,
            'jornada': None,
            'sede': None
        }
        
        repo.students.insert_one(nuevo_aspirante)
        flash(f'Aspirante {nombre} creado correctamente. Correo: {correo}', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('crear_aspirante.html')

@bp.route('/aspirante/dashboard')
def aspirante_dashboard():
    """Dashboard del aspirante."""
    if 'user' not in session or session.get('rol') != 'postulante':
        return redirect(url_for('auth.login'))
    
    # Obtener información del aspirante
    correo_usuario = session.get('user_email')
    aspirante = repo.students.find_one({'correo': correo_usuario}) if correo_usuario else None
    
    # Determinar estado de inscripción
    inscripcion_completada = aspirante and aspirante.get('estado') == 'Inscrito'
    
    return render_template('aspirante_dashboard.html', 
                         user=session.get('user'),
                         inscripcion_completada=inscripcion_completada,
                         aspirante=aspirante)

@bp.route('/aspirante/documentos/<correo>')
def descargar_documentos(correo):
    """Genera y descarga un PDF con los documentos del aspirante."""
    if 'user' not in session:
        return redirect(url_for('main.login'))
    
    # Obtener información del aspirante
    aspirante_doc = repo.students.find_one({'correo': correo})
    
    if not aspirante_doc:
        flash('Aspirante no encontrado', 'danger')
        return redirect(url_for('main.lista_aspirantes'))
    
    # Crear mapas de períodos, carreras y sedes
    periodos = list(repo.db.periods.find())
    carreras = list(repo.db.careers.find())
    sedes = list(repo.db.sedes.find())
    per_map = {p.get('id'): p.get('nombre') for p in periodos}
    car_map = {c.get('id'): c.get('nombre') for c in carreras}
    sed_map = {s.get('id'): s.get('nombre') for s in sedes}
    
    # Obtener nombres mapeados
    periodo_nombre = per_map.get(aspirante_doc.get('periodo'), 'No asignado')
    carrera_nombre = car_map.get(aspirante_doc.get('carrera'), 'No asignada')
    sede_nombre = sed_map.get(aspirante_doc.get('sede'), 'No asignada')
    
    # Crear PDF en memoria
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Contenedor de elementos
    elementos = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Centrado
    )
    elementos.append(Paragraph("DOCUMENTOS DEL ASPIRANTE", titulo_style))
    elementos.append(Spacer(1, 0.3*inch))
    
    # Información del aspirante en tabla
    datos_aspirante = [
        ['Nombre:', aspirante_doc.get('nombre', 'N/A')],
        ['Correo:', aspirante_doc.get('correo', 'N/A')],
        ['DNI:', aspirante_doc.get('dni', 'N/A')],
        ['Período:', periodo_nombre],
        ['Carrera:', carrera_nombre],
        ['Jornada:', aspirante_doc.get('jornada', 'N/A')],
        ['Sede:', sede_nombre],
        ['Estado:', aspirante_doc.get('estado', 'Pendiente')]
    ]
    
    tabla_info = Table(datos_aspirante, colWidths=[1.5*inch, 4*inch])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elementos.append(tabla_info)
    elementos.append(Spacer(1, 0.4*inch))
    
    # Sección de documentos adjuntos
    elementos.append(Paragraph("DOCUMENTOS ADJUNTOS", styles['Heading2']))
    elementos.append(Spacer(1, 0.2*inch))
    
    # Buscar documentos asociados
    documentos = list(repo.db.documents.find({'correo': correo}))
    
    if documentos:
        datos_docs = [['#', 'Tipo', 'Archivo', 'Estado', 'Observaciones']]
        for idx, doc in enumerate(documentos, 1):
            datos_docs.append([
                str(idx),
                doc.get('tipo', 'Documento'),
                doc.get('nombre_archivo', 'sin_nombre.pdf'),
                doc.get('estado', 'Pendiente'),
                doc.get('obs', 'Sin observaciones')
            ])
        
        tabla_docs = Table(datos_docs, colWidths=[0.4*inch, 1.5*inch, 1.8*inch, 1*inch, 1.8*inch])
        tabla_docs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elementos.append(tabla_docs)
    else:
        elementos.append(Paragraph("No hay documentos registrados para este aspirante.", styles['Normal']))
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    nombre_archivo = f"documentos_{aspirante_doc.get('nombre', 'aspirante').replace(' ', '_')}.pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nombre_archivo
    )