from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
import os
from .models import InMemoryAuthService, DEFAULT_DB
from .certificate import generate_certificate

# Importar el repositorio usando el patrón Bridge
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from patrones_diseño.patron_brige import create_repository

# Crear el repositorio según la configuración
USE_MONGODB = os.environ.get('USE_MONGODB', 'true').lower() == 'true'
repo = create_repository(use_mongodb=USE_MONGODB)

bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

# Servicio de autenticación
auth_service = InMemoryAuthService(DEFAULT_DB)


@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        if not correo or not contrasena:
            flash('Complete correo y contraseña', 'danger')
            return redirect(url_for('main.login'))
        usuario = auth_service.authenticate(correo, contrasena)
        if usuario is None:
            flash('Credenciales incorrectas', 'danger')
            return redirect(url_for('main.login'))
        session['user'] = usuario.nombre
        session['rol'] = usuario.get_rol()
        flash(f'Bienvenido/a, {usuario.nombre}', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Limpiar mensajes flash antiguos cuando se accede directamente al login
    session.pop('_flashes', None)
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('main.login'))


@bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    return render_template('dashboard.html', user=session.get('user'))


@bp.route('/aspirante/list')
def lista_aspirantes():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    rows = repo.list_students()
    students = [dict(r) for r in rows]
    return render_template('lista.html', students=students)


@bp.route('/aspirante/<student_id>/certificado')
def descargar_certificado(student_id):
    """Genera y descarga el certificado de inscripción de un aspirante."""
    if 'user' not in session:
        return redirect(url_for('main.login'))
    
    # Obtener datos del estudiante
    student = repo.get_student(student_id)
    if not student:
        flash('Aspirante no encontrado', 'danger')
        return redirect(url_for('main.lista_aspirantes'))
    
    # Convertir a diccionario si es necesario
    student_data = dict(student) if not isinstance(student, dict) else student
    
    # Obtener información adicional (período y carrera)
    if student_data.get('period_id'):
        period = repo.get_period(str(student_data['period_id']))
        if period:
            student_data['period_name'] = period.get('name') if isinstance(period, dict) else period['name']
    
    if student_data.get('career_id'):
        career = repo.get_career(str(student_data['career_id']))
        if career:
            student_data['career_name'] = career.get('name') if isinstance(career, dict) else career['name']
    
    # Generar el PDF
    try:
        pdf_buffer = generate_certificate(student_data)
        nombre_archivo = f"Certificado_Inscripcion_{student_data.get('nombre', 'Aspirante').replace(' ', '_')}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nombre_archivo
        )
    except Exception as e:
        flash(f'Error al generar certificado: {str(e)}', 'danger')
        return redirect(url_for('main.lista_aspirantes'))


@bp.route('/aspirante/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        periodo = request.form.get('periodo')
        carrera = request.form.get('carrera')
        apellidos = request.form.get('apellidos', '').strip()
        nombres = request.form.get('nombres', '').strip()
        correo = request.form.get('correo', '').strip()
        dni = request.form.get('dni', '').strip()
        if not periodo:
            flash('Seleccione un período', 'danger')
            return redirect(url_for('main.inscripcion'))
        if not carrera:
            flash('Seleccione una carrera', 'danger')
            return redirect(url_for('main.inscripcion'))
        if not (apellidos or nombres) or not correo:
            flash('Apellidos/Nombres y correo son obligatorios', 'danger')
            return redirect(url_for('main.inscripcion'))
        periods = repo.list_periods()
        # Buscar período por ID (funciona con int o string)
        p = next((p for p in periods if str(p['id']) == str(periodo)), None)
        if p is None:
            flash('Período no encontrado', 'danger')
            return redirect(url_for('main.inscripcion'))
        if p and not p.get('active'):
            flash('El período seleccionado no está activo.', 'danger')
            return redirect(url_for('main.inscripcion'))
        try:
            # Usar el ID como string (compatible con MongoDB y SQLite)
            period_id = str(p['id']) if p else None
            career_id = str(carrera) if carrera else None
            repo.add_student(nombre=f"{apellidos} {nombres}".strip(), correo=correo, dni=dni, period_id=period_id, inscripcion_finalizada=0, apellidos=apellidos, nombres=nombres, career_id=career_id)
            flash('Aspirante registrado correctamente', 'success')
            return redirect(url_for('main.lista_aspirantes'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('main.inscripcion'))

    # Limpiar mensajes flash antiguos cuando se accede al formulario por GET
    session.pop('_flashes', None)
    periods = repo.list_periods()
    careers = repo.list_active_careers()
    return render_template('inscripcion.html', periods=[dict(p) for p in periods], careers=[dict(c) for c in careers])
