import os
from dotenv import load_dotenv

# Carga las variables desde un archivo .env si existe
load_dotenv()

class Config:
    """Configuración base del sistema SIPU."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-para-desarrollo'
    
    # Configuración de MongoDB
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
    DATABASE_NAME = 'sipu_db'
    
    # Configuración de Flask
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False