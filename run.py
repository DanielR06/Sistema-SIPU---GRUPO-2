# refactorizacion/run.py
from sipu import create_app

app = create_app()

if __name__ == '__main__':
    # Ejecución en el puerto 5000
    app.run(debug=True, port=5000)