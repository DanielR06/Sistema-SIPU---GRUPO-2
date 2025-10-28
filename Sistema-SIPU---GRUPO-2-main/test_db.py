from db import SQLiteRepository

print('Iniciando prueba de DB...')
r = SQLiteRepository()
# listar periodos actuales
print('Periodos actuales:', [dict(p) for p in r.list_periods()])
# crear un periodo de prueba
pid = r.add_period('periodo_test_aut', 1)
print('Periodo creado id=', pid)
# crear estudiante de prueba
try:
    sid = r.add_student('Test Auto', 'testauto@example.com', '000111222')
    print('Estudiante creado id=', sid)
except Exception as e:
    print('Error creando estudiante:', e)
# listar estudiantes
students = r.list_students()
print('Estudiantes:', [dict(s) for s in students])
# limpiar: cerrar conexion
r.close()
print('Prueba DB finalizada.')
