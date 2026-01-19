# sipu/infrastructure/database.py
import os
from pymongo import MongoClient

class MongoDBClient:
    """
    Patrón Creacional: Singleton.
    Asegura una única instancia de la conexión a la base de datos.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print(">>> Inicializando conexión única a MongoDB (Singleton)...")
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            
            # Configuración
            uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = "sipu_db"
            
            # Conexión real
            cls._instance.client = MongoClient(uri)
            cls._instance.db = cls._instance.client[db_name]
            
        return cls._instance

    @property
    def database(self):
        """Retorna la referencia a la base de datos."""
        return self.db

    def close(self):
        """Cierra la conexión."""
        self.client.close()