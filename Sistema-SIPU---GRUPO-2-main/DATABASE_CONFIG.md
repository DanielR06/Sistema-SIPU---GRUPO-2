# Configuración de Base de Datos - SIPU

## MongoDB (Configuración por Defecto)

El sistema ahora usa **MongoDB** por defecto para una mejor escalabilidad y rendimiento.

### Opción 1: MongoDB Local

1. **Instalar MongoDB Community Edition:**
   - Descarga desde: https://www.mongodb.com/try/download/community
   - O usa Docker: `docker run -d -p 27017:27017 --name mongodb mongo:latest`

2. **El sistema se conectará automáticamente a:**
   - URI: `mongodb://localhost:27017/`
   - Base de datos: `sipu_db`

### Opción 2: MongoDB Atlas (Cloud - Recomendado)

1. **Crear cuenta gratuita:**
   - Visita: https://www.mongodb.com/cloud/atlas/register
   - Crea un cluster gratuito (M0)

2. **Obtener URI de conexión:**
   - En Atlas, ve a "Connect" → "Connect your application"
   - Copia la connection string
   - Reemplaza `<password>` con tu contraseña

3. **Configurar variables de entorno:**
   ```powershell
   $env:MONGODB_URI = "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
   $env:MONGODB_DB = "sipu_db"
   ```

### Variables de Entorno Disponibles

```powershell
# Usar MongoDB (por defecto: true)
$env:USE_MONGODB = "true"

# URI de MongoDB (por defecto: localhost)
$env:MONGODB_URI = "mongodb://localhost:27017/"

# Nombre de la base de datos (por defecto: sipu_db)
$env:MONGODB_DB = "sipu_db"

# Secret key de Flask
$env:FLASK_SECRET = "tu-clave-secreta-aqui"
```

## SQLite (Alternativa)

Si prefieres usar SQLite en lugar de MongoDB:

```powershell
$env:USE_MONGODB = "false"
```

El sistema creará automáticamente el archivo `sipu.db` en la raíz del proyecto.

## Ventajas de MongoDB

✅ **Escalabilidad**: Crece con tu aplicación  
✅ **Flexibilidad**: Esquema flexible para cambios futuros  
✅ **Rendimiento**: Mejor para grandes volúmenes de datos  
✅ **Cloud Ready**: Fácil integración con MongoDB Atlas  
✅ **Consultas Avanzadas**: Aggregation pipeline potente  

## Características Implementadas

- ✅ Gestión de estudiantes/aspirantes
- ✅ Gestión de períodos académicos
- ✅ Gestión de carreras
- ✅ Gestión de documentos
- ✅ Índices para optimización
- ✅ Validación de datos únicos (correo)
- ✅ Joins automáticos (lookups) para relaciones

## Ejecutar el Sistema

```powershell
# Con MongoDB local (por defecto)
python run.py

# Con MongoDB Atlas
$env:MONGODB_URI = "mongodb+srv://usuario:password@cluster.mongodb.net/"
python run.py

# Con SQLite
$env:USE_MONGODB = "false"
python run.py
```

## Verificar Conexión

El sistema mostrará en los logs al iniciar qué base de datos está usando.
