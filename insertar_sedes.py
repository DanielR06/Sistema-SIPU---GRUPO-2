"""
Script para insertar sedes en MongoDB
"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['sipu_db']

# Verificar si ya existen sedes
if db.sedes.count_documents({}) > 0:
    print("✅ Las sedes ya existen en la BD")
else:
    sedes = [
        {
            'id': 'principal',
            'nombre': 'Sede Principal'
        },
        {
            'id': 'norte',
            'nombre': 'Sede Norte'
        },
        {
            'id': 'sur',
            'nombre': 'Sede Sur'
        },
        {
            'id': 'este',
            'nombre': 'Sede Este'
        }
    ]
    
    result = db.sedes.insert_many(sedes)
    print(f"✅ {len(result.inserted_ids)} sedes insertadas correctamente")
    print("Sedes creadas:")
    for s in db.sedes.find():
        print(f"  - {s['nombre']}")
