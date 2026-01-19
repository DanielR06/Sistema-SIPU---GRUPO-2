# refactorizacion/sipu/__init__.py
from flask import Flask
import os

def create_app():
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static')
    
    app.secret_key = os.urandom(24)

    # CORRECCIÓN: Importa desde la nueva ruta de infraestructura
    from .infrastructure.routes.sipu_routes import bp as main_bp
    from .infrastructure.routes.auth_routes import bp as auth_bp
    
    # Registro de Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app