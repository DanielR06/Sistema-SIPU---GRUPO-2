# Patrón de Diseño Observer - Sistema SIPU

## 📋 Descripción

Implementación profesional del **Patrón Observer** aplicado al Sistema de Inscripción y Postulación Universitaria (SIPU). Este patrón permite que múltiples componentes del sistema reaccionen automáticamente a eventos sin acoplamiento directo.

## 🎯 Objetivos de Aprendizaje

### Fundamentos de POO Aplicados:

1. **Abstracción**
   - Interfaces `Observer` y `Subject` definen contratos claros
   - Clase `Event` encapsula la información del evento

2. **Encapsulamiento**
   - Propiedades privadas protegidas con `@property`
   - Estado interno de observadores encapsulado
   - Datos de eventos inmutables (retornan copias)

3. **Herencia**
   - `ABC` (Abstract Base Class) para interfaces
   - Observadores concretos heredan de `Observer`

4. **Polimorfismo**
   - Múltiples implementaciones de `Observer.update()`
   - Cada observador responde diferente al mismo evento

5. **Inyección de Dependencias**
   - `Subject` recibe observadores externamente
   - `DatabaseObserver` recibe el repositorio

## 🏗️ Arquitectura

```
Observer Pattern
├── Interfaces (ABC)
│   ├── Observer (abstracta)
│   └── Subject (concreta)
│
├── Modelos
│   ├── Event
│   └── EventType (Enum)
│
├── Observadores Concretos
│   ├── EmailNotificationObserver
│   ├── LoggingObserver
│   ├── StatisticsObserver
│   └── DatabaseObserver
│
└── Gestor
    └── SIPUEventManager (Singleton)
```

## 📦 Componentes Principales

### 1. Event (Modelo de Evento)
```python
event = Event(
    event_type=EventType.STUDENT_REGISTERED,
    data={'nombre': 'Juan', 'correo': 'juan@email.com'},
    source='SIPU_System'
)
```

**Características:**
- Inmutable (propiedades read-only)
- Timestamp automático
- Serialización a dict/JSON

### 2. Observer (Interfaz Abstracta)
```python
class Observer(ABC):
    @abstractmethod
    def update(self, event: Event) -> None:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
```

### 3. Subject (Sujeto Observable)
```python
subject = Subject("SIPU")
subject.attach(observer1)
subject.attach(observer2)
subject.notify(event)
```

**Funcionalidades:**
- Registro/desregistro de observadores
- Notificación a todos los observadores
- Historial de eventos (últimos 100)
- Manejo de errores en observadores

### 4. Observadores Concretos

#### EmailNotificationObserver
- **Propósito**: Enviar notificaciones por correo
- **Eventos**: Registro, aprobación/rechazo documentos, certificados
- **Implementación**: Simula envío SMTP (preparado para producción)

#### LoggingObserver
- **Propósito**: Auditoría y registro de eventos
- **Formato**: JSON estructurado con timestamp
- **Archivo**: `sipu_events.log`

#### StatisticsObserver
- **Propósito**: Métricas y análisis
- **Métricas**: Contadores por tipo de evento
- **Funcionalidad**: Reporte de estadísticas

#### DatabaseObserver
- **Propósito**: Persistencia de eventos
- **Integración**: MongoDB/SQLite Repository
- **Uso**: Historial completo en BD

### 5. SIPUEventManager (Singleton)
```python
event_manager = SIPUEventManager()
event_manager.add_observer(email_observer)
event_manager.emit_event(EventType.STUDENT_REGISTERED, data)
```

**Características:**
- Patrón Singleton (única instancia)
- API simple para emisión de eventos
- Gestión centralizada de observadores

## 🚀 Uso Básico

### Configuración Inicial
```python
from patron_de_diseño.Observer import (
    SIPUEventManager, EventType,
    EmailNotificationObserver,
    LoggingObserver,
    StatisticsObserver
)

# 1. Crear gestor (Singleton)
event_manager = SIPUEventManager()

# 2. Crear observadores
email_obs = EmailNotificationObserver()
log_obs = LoggingObserver()
stats_obs = StatisticsObserver()

# 3. Registrar observadores
event_manager.add_observer(email_obs)
event_manager.add_observer(log_obs)
event_manager.add_observer(stats_obs)
```

### Emisión de Eventos
```python
# Cuando se registra un estudiante
event_manager.emit_event(
    EventType.STUDENT_REGISTERED,
    {
        'nombre': 'María García',
        'correo': 'maria@email.com',
        'carrera': 'Ingeniería Civil',
        'periodo': '2025-1'
    }
)

# Cuando se aprueba un documento
event_manager.emit_event(
    EventType.DOCUMENT_APPROVED,
    {
        'nombre': 'Juan Pérez',
        'correo': 'juan@email.com',
        'documento': 'DNI'
    }
)
```

## 🔌 Integración con SIPU

### En routes.py
```python
from patron_de_diseño.Observer import SIPUEventManager, EventType

# Inicializar en app startup
event_manager = SIPUEventManager()

@bp.route('/aspirante/inscripcion', methods=['POST'])
def inscripcion():
    # ... código de registro ...
    
    # Emitir evento después de guardar
    event_manager.emit_event(
        EventType.STUDENT_REGISTERED,
        {
            'nombre': nombre,
            'correo': correo,
            'carrera': career_name,
            'periodo': period_name
        }
    )
    
    return redirect(url_for('main.lista_aspirantes'))
```

## 📊 Tipos de Eventos

| EventType | Descripción | Datos Típicos |
|-----------|-------------|---------------|
| `STUDENT_REGISTERED` | Nuevo estudiante inscrito | nombre, correo, carrera, periodo |
| `STUDENT_UPDATED` | Datos actualizados | student_id, campos_modificados |
| `DOCUMENT_UPLOADED` | Documento subido | nombre, documento, fecha |
| `DOCUMENT_APPROVED` | Documento aprobado | nombre, documento, aprobador |
| `DOCUMENT_REJECTED` | Documento rechazado | nombre, documento, razón |
| `PERIOD_ACTIVATED` | Período activado | period_name, fecha_inicio |
| `PERIOD_DEACTIVATED` | Período desactivado | period_name, fecha_fin |
| `CAREER_ADDED` | Nueva carrera agregada | career_name, activa |
| `CERTIFICATE_GENERATED` | Certificado generado | nombre, certificado_id |

## 🧪 Demostración

### Ejecutar Demo Básica
```bash
cd "patron de diseño"
python Observer.py
```

### Ejecutar Demo con Integración
```bash
python integration_example.py
```

## ✅ Ventajas del Patrón

1. **Desacoplamiento**: Los módulos no necesitan conocerse entre sí
2. **Extensibilidad**: Nuevos observadores sin modificar código
3. **Reusabilidad**: Observadores reutilizables en diferentes contextos
4. **Mantenibilidad**: Responsabilidad única por observador
5. **Escalabilidad**: Múltiples observadores por evento
6. **Testing**: Fácil de probar independientemente

## 🎓 Conceptos Avanzados Implementados

### 1. Patrón Singleton
```python
class SIPUEventManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Enum para Tipos
```python
class EventType(Enum):
    STUDENT_REGISTERED = "student_registered"
    # ...
```

### 3. Properties (Getters)
```python
@property
def timestamp(self) -> datetime:
    return self._timestamp
```

### 4. Abstract Base Classes
```python
class Observer(ABC):
    @abstractmethod
    def update(self, event: Event) -> None:
        pass
```

### 5. Type Hints
```python
def emit_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
    # ...
```

## 📈 Casos de Uso Reales

### 1. Notificaciones Email
- ✅ Confirmación de inscripción
- ✅ Aprobación/rechazo de documentos
- ✅ Certificado disponible

### 2. Auditoría
- ✅ Log de todos los eventos
- ✅ Trazabilidad completa
- ✅ Cumplimiento normativo

### 3. Análisis
- ✅ Métricas en tiempo real
- ✅ Reportes de uso
- ✅ Dashboard de estadísticas

### 4. Persistencia
- ✅ Historial en base de datos
- ✅ Recuperación de eventos
- ✅ Análisis histórico

## 🔧 Configuración de Producción

### Setup con Flask
```python
# En sipu/__init__.py
from patron_de_diseño.Observer import setup_sipu_observers

def create_app():
    app = Flask(__name__)
    
    # Configurar observadores
    with app.app_context():
        event_manager = setup_sipu_observers()
    
    return app
```

## 📝 Notas de Implementación

- **Thread-Safety**: Considerar locks para ambientes multi-thread
- **Performance**: Límite de 100 eventos en historial
- **Error Handling**: Observadores fallidos no afectan a otros
- **Logging**: Eventos registrados en `sipu_events.log`
- **Testing**: Cada observador es testeable independientemente

## 🎯 Conclusión

Este patrón Observer demuestra:
- ✅ Uso avanzado de POO
- ✅ Patrones de diseño profesionales
- ✅ Código limpio y mantenible
- ✅ Arquitectura escalable
- ✅ Integración real con el sistema

---

**Autor**: Sistema SIPU - Grupo 2  
**Curso**: Programación Orientada a Objetos  
**Fecha**: Diciembre 2025
