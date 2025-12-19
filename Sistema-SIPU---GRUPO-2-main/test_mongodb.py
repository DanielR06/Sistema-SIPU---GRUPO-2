"""Script para verificar y probar la conexión a MongoDB."""
import os
import sys

def test_mongodb_connection():
    """Prueba la conexión a MongoDB."""
    try:
        from pymongo import MongoClient
        
        # Obtener URI de las variables de entorno o usar localhost
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.environ.get('MONGODB_DB', 'sipu_db')
        
        print(f"🔍 Probando conexión a MongoDB...")
        print(f"   URI: {mongodb_uri}")
        print(f"   Base de datos: {db_name}")
        
        # Intentar conectar
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        
        print("✅ Conexión exitosa a MongoDB")
        
        # Mostrar información del servidor
        server_info = client.server_info()
        print(f"   Versión MongoDB: {server_info.get('version', 'N/A')}")
        
        # Listar bases de datos
        dbs = client.list_database_names()
        print(f"   Bases de datos disponibles: {', '.join(dbs)}")
        
        # Verificar colecciones en nuestra BD
        db = client[db_name]
        collections = db.list_collection_names()
        if collections:
            print(f"   Colecciones en '{db_name}': {', '.join(collections)}")
        else:
            print(f"   Base de datos '{db_name}' está vacía (se creará al insertar datos)")
        
        client.close()
        return True
        
    except ImportError:
        print("❌ ERROR: pymongo no está instalado")
        print("   Ejecuta: pip install pymongo")
        return False
        
    except Exception as e:
        print(f"❌ ERROR al conectar a MongoDB: {str(e)}")
        print("\n💡 Soluciones:")
        print("   1. Verifica que MongoDB esté ejecutándose")
        print("   2. Para MongoDB local: docker run -d -p 27017:27017 mongo")
        print("   3. Para MongoDB Atlas: configura $env:MONGODB_URI con tu connection string")
        print("   4. Para usar SQLite en su lugar: $env:USE_MONGODB = 'false'")
        return False


def test_repository():
    """Prueba el repositorio MongoDB."""
    try:
        from sipu.mongo_repository import MongoDBRepository
        
        print("\n🔍 Probando MongoDBRepository...")
        
        repo = MongoDBRepository()
        
        # Probar listado de carreras
        careers = repo.list_careers()
        print(f"✅ Carreras disponibles: {len(careers)}")
        for career in careers[:3]:  # Mostrar las primeras 3
            print(f"   - {career.get('name', 'N/A')}")
        
        # Probar listado de períodos
        periods = repo.list_periods()
        print(f"✅ Períodos registrados: {len(periods)}")
        
        # Probar listado de estudiantes
        students = repo.list_students()
        print(f"✅ Estudiantes registrados: {len(students)}")
        
        repo.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR en el repositorio: {str(e)}")
        return False


def main():
    """Función principal."""
    print("=" * 60)
    print("   SIPU - Verificación de Conexión MongoDB")
    print("=" * 60)
    
    # Verificar conexión
    if not test_mongodb_connection():
        sys.exit(1)
    
    # Probar repositorio
    if not test_repository():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Todas las pruebas pasaron correctamente")
    print("   El sistema está listo para usar MongoDB")
    print("=" * 60)


if __name__ == '__main__':
    main()
