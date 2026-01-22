# refactorizacion/seed_db.py
from sipu.infrastructure.database import MongoDBClient

def seed_admin(db):
    """Crea el usuario administrador inicial."""
    admin_user = {
        "nombre": "Admin Principal",
        "correo": "admin1",
        "contrasena": "123",
        "rol": "admin",
        "estado": "Activo"
    }
    # Usamos update_one con upsert=True para no duplicar si el usuario ya existe
    db.students.update_one(
        {"correo": "admin1"}, 
        {"$set": admin_user}, 
        upsert=True
    )
    print(">>> Usuario 'admin1' configurado.")

def seed_catalogos(db):
    """Crea los datos para los desplegables de inscripción."""
    # Configuración de Períodos
    periodos = [
        {"id": "2025-1", "nombre": "2025 - Primer Período", "activo": True},
        {"id": "2025-2", "nombre": "2025 - Segundo Período", "activo": True}
    ]
    db.periods.delete_many({})  # Limpiamos para evitar duplicados
    db.periods.insert_many(periodos)
    
    # Configuración de Carreras
    carreras = [
        {"id": "is", "nombre": "Ingeniería de Software"},
        {"id": "ic", "nombre": "Ingeniería Civil"},
        {"id": "it", "nombre": "Tecnologías de la Información"}
    ]
    db.careers.delete_many({})
    db.careers.insert_many(carreras)
    
    # Configuración de Sedes
    sedes = [
        {"id": "principal", "nombre": "Sede Principal"},
        {"id": "norte", "nombre": "Sede Norte"},
        {"id": "sur", "nombre": "Sede Sur"},
        {"id": "este", "nombre": "Sede Este"}
    ]
    db.sedes.delete_many({})
    db.sedes.insert_many(sedes)
    
    print(">>> Catálogos de Período, Carrera y Sede configurados.")

def main():
    print(">>> Iniciando proceso de seed...")
    # Obtenemos la conexión única a través del Singleton configurado en infrastructure
    client = MongoDBClient()
    db = client.database
    
    seed_admin(db)
    seed_catalogos(db)
    
    print(">>> Base de datos SIPU inicializada exitosamente.")

if __name__ == "__main__":
    main()