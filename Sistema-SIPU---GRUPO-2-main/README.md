# Sistema-SIPU (Grupo 2)

Proyecto demo que implementa un prototipo de sistema de inscripción y postulación
universitaria (SIPU) con enfoque en Programación Orientada a Objetos (POO) y
patrones básicos (abstracción, herencia, polimorfismo, interfaces, inyección de
dependencias). Incluye una interfaz gráfica de ejemplo con CustomTkinter y
persistencia ligera con SQLite.

## Estructura del proyecto

- `clases.py`  — Definiciones de dominio: `Usuario` (ABC), `Administrador`, `Aspirante`,
	`AuthService` (interfaz) y `InMemoryAuthService`.
- `main.py`    — Interfaz gráfica con CustomTkinter. Login -> panel principal.
- `db.py`      — Repositorio `SQLiteRepository` con tablas `students` y `documents`.
- `requirements.txt` — Dependencias para la GUI (`customtkinter`).

## Requisitos

- Python 3.8+ (recomendado).
- `tkinter` (normalmente viene con Python en Windows). Si no está, instale la
	versión correspondiente a su sistema.

## Instalación (Windows PowerShell)

1. (Opcional) Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2. Instalar dependencias:

```powershell
python -m pip install -r "c:\\Users\\ASUS\\Downloads\\Sistema-SIPU---GRUPO-2-main\\Sistema-SIPU---GRUPO-2-main\\requirements.txt"
```

Nota: `customtkinter` es una librería de interfaz moderna que requiere `tkinter`.

## Ejecución

Desde PowerShell, en la carpeta del proyecto:

```powershell
# ejecutar la interfaz
python "c:\\Users\\ASUS\\Downloads\\Sistema-SIPU---GRUPO-2-main\\Sistema-SIPU---GRUPO-2-main\\main.py"
```

## Credenciales de prueba

En `clases.py` hay una base de datos en memoria (`DEFAULT_DB`) con usuarios de
ejemplo:

- Admin: correo `admin1`, contraseña `123` (rol: admin)
- Postulante: correo `daniel`, contraseña `software1` (rol: postulante)

Usa estas credenciales en la pantalla de login para entrar al panel.

## Qué hace el prototipo

- Login con `AuthService` inyectado (poco acoplado).
- Al autenticarse se crea (si no existe) la base de datos SQLite `sipu.db` y se
	abre un panel principal con un menú (Aspirante, Seguridad, Salir).
- Vista "Aspirante": permite registrar nuevos aspirantes (nombre, correo, DNI)
	y listar los ya registrados (persistidos en SQLite).

## Arquitectura y patrones aplicados

- Abstracción: `Usuario` implementado como clase abstracta (ABC).
- Herencia / Polimorfismo: `Administrador` y `Aspirante` heredan de `Usuario` y
	sobrescriben comportamiento (ej. `get_rol()`).
- Interfaces: `AuthService` como contrato para autenticación; `InMemoryAuthService`
	es una implementación concreta.
- Inyección de dependencias: la GUI recibe el servicio de autenticación y
	crea/usa un repositorio `SQLiteRepository` para persistencia.
- Encapsulamiento y propiedades: uso de `@property` en `Evaluacion` y `Usuario`.

## Notas de seguridad y producción

- Este proyecto es un prototipo educativo. No almacena contraseñas de forma
	segura (texto plano). Para producción, use hashing (bcrypt/argon2) y SSL.
- Valide y sanee entradas: actualmente las validaciones son básicas.

## Próximos pasos recomendados

- Añadir gestión de documentos en la UI (subida y listado por estudiante).
- Implementar hashing de contraseñas y una migración de la base de datos.
- Añadir tests unitarios (`pytest`) para `SQLiteRepository` y `AuthService`.

Si quieres, puedo implementar cualquiera de los siguientes ahora:
- Añadir la UI para gestionar documentos (subida/descarga/listado).
- Implementar hashing de contraseñas y migración de la DB.
- Añadir tests unitarios automáticos y ejecutarlos.

---

Creado automáticamente por el asistente. Fecha de edición: 2025-10-27.
# Sistema-SIPU---GRUPO-2
