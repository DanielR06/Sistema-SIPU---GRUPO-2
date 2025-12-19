"""Script para inicializar datos de ejemplo en la base de datos."""
import os
from datetime import datetime, timedelta

def initialize_sample_data():
    """Inserta datos de ejemplo en la base de datos."""
    try:
        from patrones_diseño.patron_brige import create_repository
        
        print("=" * 60)
        print("   Inicializando datos de ejemplo en la base de datos")
        print("=" * 60)
        
        # Usar MongoDB por defecto para inicialización
        repo = create_repository(use_mongodb=True)
        
        # Verificar si ya existen datos
        existing_periods = repo.list_periods()
        if len(existing_periods) > 0:
            print("\n⚠️  Ya existen períodos en la base de datos")
            response = input("¿Deseas agregar más períodos de ejemplo? (s/n): ")
            if response.lower() != 's':
                print("❌ Operación cancelada")
                return
        
        # Crear períodos de ejemplo
        print("\n📅 Creando períodos académicos...")
        
        today = datetime.now()
        
        periods = [
            {
                'name': '2025-1',
                'active': True,
                'start_date': today.strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(days=180)).strftime('%Y-%m-%d')
            },
            {
                'name': '2025-2',
                'active': False,
                'start_date': (today + timedelta(days=180)).strftime('%Y-%m-%d'),
                'end_date': (today + timedelta(days=360)).strftime('%Y-%m-%d')
            },
            {
                'name': '2024-2',
                'active': False,
                'start_date': (today - timedelta(days=180)).strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d')
            }
        ]
        
        for period in periods:
            period_id = repo.add_period(
                name=period['name'],
                active=1 if period['active'] else 0,
                start_date=period['start_date'],
                end_date=period['end_date']
            )
            status = "✅ ACTIVO" if period['active'] else "⏸️  Inactivo"
            print(f"   {status} - {period['name']} ({period['start_date']} → {period['end_date']})")
        
        # Mostrar resumen
        print("\n📊 Resumen de la base de datos:")
        
        careers = repo.list_careers()
        print(f"   ✅ Carreras: {len(careers)}")
        for career in careers:
            print(f"      - {career['name']}")
        
        all_periods = repo.list_periods()
        print(f"\n   ✅ Períodos: {len(all_periods)}")
        for p in all_periods:
            status = "🟢 ACTIVO" if p.get('active') else "⚪ Inactivo"
            print(f"      {status} {p['name']}")
        
        students = repo.list_students()
        print(f"\n   ✅ Estudiantes: {len(students)}")
        
        repo.close()
        
        print("\n" + "=" * 60)
        print("✅ Datos de ejemplo creados correctamente")
        print("   El sistema está listo para usar")
        print("=" * 60)
        print("\n💡 Ahora puedes:")
        print("   1. Ejecutar: python run.py")
        print("   2. Abrir: http://127.0.0.1:5000")
        print("   3. Login: admin@sipu.com / admin123")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n💡 Asegúrate de:")
        print("   1. MongoDB está ejecutándose")
        print("   2. Las dependencias están instaladas: pip install pymongo")


if __name__ == '__main__':
    initialize_sample_data()
