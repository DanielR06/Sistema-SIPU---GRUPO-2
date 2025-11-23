import time
import sys
from sipu.repository import SQLiteRepository

# 1) Aseguramos que exista al menos un periodo activo
repo = SQLiteRepository()
periods = repo.list_periods()
if not periods:
    pid = repo.add_period('Periodo Prueba', active=1)
    print('Periodo creado id=', pid)
else:
    print('Periodos existentes:', [dict(p) for p in periods])

# 2) Comprobamos endpoints via HTTP usando cookiejar
import http.cookiejar, urllib.request, urllib.parse

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
base = 'http://127.0.0.1:5000'

# GET /
print('\nGET /')
resp = opener.open(base + '/')
print('status', resp.getcode())
html = resp.read(800).decode(errors='replace')
print(html[:300])

# POST login
print('\nPOST / (login)')
login_data = urllib.parse.urlencode({'correo': 'admin1', 'contrasena': '123'}).encode()
resp = opener.open(base + '/', data=login_data)
print('after login url:', resp.geturl(), 'status', getattr(resp, 'status', resp.getcode()))

# GET inscripcion
print('\nGET /aspirante/inscripcion')
resp = opener.open(base + '/aspirante/inscripcion')
print('status', resp.getcode())
ins_html = resp.read(1000).decode(errors='replace')
print(ins_html[:400])

# POST inscripcion (usando periodo id 1 or first period id)
print('\nPOST /aspirante/inscripcion')
periods = repo.list_periods()
pid = periods[0]['id'] if periods else ''
post_data = urllib.parse.urlencode({
    'periodo': str(pid),
    'apellidos': 'Prueba',
    'nombres': 'Usuario',
    'correo': 'prueba+test@example.com',
    'dni': '12345678'
}).encode()
resp = opener.open(base + '/aspirante/inscripcion', data=post_data)
print('after inscripcion url:', resp.geturl(), 'status', getattr(resp, 'status', resp.getcode()))

# GET lista
print('\nGET /aspirante/list')
resp = opener.open(base + '/aspirante/list')
print('status', resp.getcode())
list_html = resp.read(2000).decode(errors='replace')
print(list_html[:800])

print('\nFinished test')
