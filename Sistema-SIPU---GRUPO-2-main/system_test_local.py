from sipu import create_app
from sipu.repository import SQLiteRepository

app = create_app()
with app.app_context():
    repo = SQLiteRepository()
    if not repo.list_periods():
        pid = repo.add_period('periodo_test_local', active=1)
        print('Periodo creado id=', pid)
    else:
        print('Periodos existentes:', [dict(p) for p in repo.list_periods()])

with app.test_client() as client:
    print('\nGET /')
    r = client.get('/')
    print('status', r.status_code)
    print(r.data[:300].decode(errors='replace'))

    print('\nPOST / (login)')
    r = client.post('/', data={'correo': 'admin1', 'contrasena': '123'}, follow_redirects=True)
    print('login status', r.status_code)
    print('after login path:', r.request.path)

    print('\nGET /aspirante/inscripcion')
    r = client.get('/aspirante/inscripcion')
    print('status', r.status_code)
    print(r.data[:400].decode(errors='replace'))

    print('\nPOST /aspirante/inscripcion')
    periods = repo.list_periods()
    pid = periods[0]['id'] if periods else ''
    r = client.post('/aspirante/inscripcion', data={
        'periodo': str(pid),
        'apellidos': 'Local',
        'nombres': 'Tester',
        'correo': 'local+test@example.com',
        'dni': '87654321'
    }, follow_redirects=True)
    print('inscripcion status', r.status_code)
    print('after inscripcion path:', r.request.path)

    print('\nGET /aspirante/list')
    r = client.get('/aspirante/list')
    print('list status', r.status_code)
    print(r.data[:800].decode(errors='replace'))

print('\nLocal test finished')
