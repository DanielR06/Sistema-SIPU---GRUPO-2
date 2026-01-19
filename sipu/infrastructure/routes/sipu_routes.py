from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from ...application.services import SipuService
from ..repositories import MongoSipuRepository

# Inicializamos el repositorio y el servicio (Unidad 2: Inyección de Dependencias)
# En un entorno profesional, esto se haría en un 'App Factory'
repo = MongoSipuRepository()
sipu_service = SipuService(repo)

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        
        # El servicio maneja la autenticación y la cadena de responsabilidad interna
        usuario = sipu_service.autenticar_usuario(correo, contrasena)
        
        if usuario:
            session['user'] = usuario.nombre
            session['rol'] = usuario.get_rol()
            flash(f'Bienvenido/a, {usuario.nombre}', 'success')
            return redirect(url_for('main.dashboard'))
        
        flash('Credenciales incorrectas o datos inválidos', 'danger')
        return redirect(url_for('main.login'))
    
    return render_template('login.html')

@bp.route('/aspirante/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        # El servicio procesa los datos del formulario y devuelve el resultado
        exito, mensaje = sipu_service.procesar_inscripcion(request.form)
        
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('main.lista_aspirantes'))
        
        flash(mensaje, 'danger')
        return redirect(url_for('main.inscripcion'))

    # CORRECTO: Pedimos los catálogos al servicio
    periods = list(repo.db.periods.find({"activo": True})) 
    careers = list(repo.db.careers.find()) # Las carreras suelen estar todas visibles
    
    return render_template('inscripcion.html', periods=periods, careers=careers)

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
        return redirect(url_for('main.login'))
        
    return render_template('dashboard.html', user=session.get('user'))