from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ...application.services import SipuService
from ..repositories import MongoSipuRepository

# Configuración del Blueprint
bp = Blueprint('auth', __name__)

# Inyección de dependencias (Unidad 2)
# Nota: Usamos la misma instancia del repositorio que en sipu_routes
repo = MongoSipuRepository()
sipu_service = SipuService(repo)

@bp.route('/', methods=['GET', 'POST'])
def login():
    """Ruta de acceso principal (Login)."""
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        
        # Delegamos la autenticación y validación (Chain of Responsibility) al servicio
        # Esto cumple con SRP (Responsabilidad Única)
        usuario = sipu_service.autenticar_usuario(correo, contrasena)
        
        if usuario:
            # Guardamos datos mínimos en la sesión (Encapsulamiento)
            session['user'] = usuario.nombre
            session['rol'] = usuario.get_rol()
            flash(f'Bienvenido/a, {usuario.nombre}', 'success')
            return redirect(url_for('main.dashboard'))
        
        flash('Credenciales incorrectas o datos no válidos', 'danger')
        return redirect(url_for('auth.login'))
    
    # Limpiar flashes antiguos al entrar al login
    session.pop('_flashes', None)
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))