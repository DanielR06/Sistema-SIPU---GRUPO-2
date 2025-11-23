import os
from flask import Flask


def create_app():
    """Factory que crea y configura la aplicación Flask."""
    # template_folder y static_folder apuntan a las carpetas dentro del paquete
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-key')

    # Registrar blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app


# atajo para ejecutarlo desde run.py
app = create_app()
