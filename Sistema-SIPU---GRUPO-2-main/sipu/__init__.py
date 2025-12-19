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

    # Inicializar sistema de observadores
    try:
        from .observer_integration import initialize_observers
        from .routes import repo
        initialize_observers(repository=repo)
    except Exception as e:
        print(f"⚠️ No se pudo inicializar el sistema Observer: {e}")

    # Inicializar sistema de singletons
    try:
        from .singleton_integration import initialize_singletons
        initialize_singletons()
    except Exception as e:
        print(f"⚠️ No se pudo inicializar el sistema Singleton: {e}")

    # Inicializar sistema Chain of Responsibility
    try:
        from .chain_integration import initialize_chain
        initialize_chain()
    except Exception as e:
        print(f"⚠️ No se pudo inicializar el sistema Chain of Responsibility: {e}")

    # Inicializar sistema Bridge
    try:
        from .bridge_integration import initialize_bridge
        initialize_bridge()
    except Exception as e:
        print(f"⚠️ No se pudo inicializar el sistema Bridge: {e}")

    return app


# atajo para ejecutarlo desde run.py
app = create_app()
