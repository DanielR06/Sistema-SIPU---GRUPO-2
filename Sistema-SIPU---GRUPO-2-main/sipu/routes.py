from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .repository import SQLiteRepository
from .models import InMemoryAuthService, DEFAULT_DB

bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

# Inicializamos repositorio y servicio de autenticación aquí (simple)
repo = SQLiteRepository()
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


@bp.route('/aspirante/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        periodo = request.form.get('periodo')
        apellidos = request.form.get('apellidos', '').strip()
        nombres = request.form.get('nombres', '').strip()
        correo = request.form.get('correo', '').strip()
        dni = request.form.get('dni', '').strip()
        if not periodo:
            flash('Seleccione un período', 'danger')
            return redirect(url_for('main.inscripcion'))
        if not (apellidos or nombres) or not correo:
            flash('Apellidos/Nombres y correo son obligatorios', 'danger')
            return redirect(url_for('main.inscripcion'))
        periods = repo.list_periods()
        try:
            idx = int(periodo)
            p = next((p for p in periods if p['id'] == idx), None)
        except Exception:
            p = None
        if p and not p['active']:
            flash('El período seleccionado no está activo.', 'danger')
            return redirect(url_for('main.inscripcion'))
        try:
            repo.add_student(nombre=f"{apellidos} {nombres}".strip(), correo=correo, dni=dni, period_id=(p['id'] if p else None), inscripcion_finalizada=0, apellidos=apellidos, nombres=nombres)
            flash('Aspirante registrado correctamente', 'success')
            return redirect(url_for('main.lista_aspirantes'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('main.inscripcion'))

    periods = repo.list_periods()
    return render_template('inscripcion.html', periods=[dict(p) for p in periods])
