from ..domain.models import Aspirante
from ..domain.interfaces import ISipuRepository


class SipuService:
    """
    Capa de Aplicación: Orquestador de la lógica de negocio.
    Aquí aplicamos Inyección de Dependencias (Unidad 2).
    """

    def __init__(self, repository: ISipuRepository):
        # Inyectamos el repositorio (DIP)
        self.repository = repository
        
    def obtener_periodos_activos(self):
        """Llama al repositorio para obtener los periodos de la DB."""
        return self.repository.obtener_periodos()

    def obtener_carreras_activas(self):
        """Llama al repositorio para obtener las carreras de la DB."""
        return self.repository.obtener_carreras()
    
    def obtener_lista_aspirantes(self):
        """
        Caso de Uso: Recuperar todos los aspirantes para mostrarlos en la tabla.
        Llama al repositorio para obtener los datos crudos.
        """
        todos = self.repository.listar_estudiantes_crudos()
        # Filtramos: solo incluimos si el rol NO es 'admin'
        aspirantes = [u for u in todos if u.get('rol') != 'admin']
        return aspirantes
    
    def autenticar_usuario(self, correo: str, contrasena: str):
        """
        Lógica de autenticación que desacopla la UI de la base de datos.
        """
        # Buscamos el usuario directamente en la colección de estudiantes
        # para obtener todos los datos incluyendo la contraseña
        usuario_doc = self.repository.students.find_one({'correo': correo})
        
        if usuario_doc and usuario_doc.get('contrasena') == contrasena:
            # Creamos el objeto de dominio apropiado
            if usuario_doc.get('rol') == 'admin':
                from ..domain.models import Administrador
                return Administrador(nombre=usuario_doc['nombre'], correo=usuario_doc['correo'])
            else:
                aspirante = Aspirante(nombre=usuario_doc['nombre'], correo=usuario_doc['correo'])
                aspirante.estado = usuario_doc.get('estado', 'Pendiente')
                return aspirante
        return None
    def registrar_nuevo_aspirante(self, nombre: str, correo: str) -> bool:
        """
        Funcionalidad: Registro de usuario.
        Mantenemos la lógica de crear un aspirante pero usando objetos.
        """
        # 1. Verificamos si ya existe
        existente = self.repository.obtener_aspirante_por_correo(correo)
        if existente:
            return False
        
        # 2. Creamos el objeto de dominio (Unidad 1)
        nuevo_aspirante = Aspirante(nombre=nombre, correo=correo)
        
        # 3. Guardamos a través del repositorio (Abstracción)
        return self.repository.guardar_aspirante(nuevo_aspirante)

    def procesar_aprobacion(self, correo_aspirante: str, estado: str, obs: str):
        """
        Aquí es donde integraremos el Chain of Responsibility más adelante.
        """
        aspirante = self.repository.obtener_aspirante_por_correo(correo_aspirante)
        if aspirante:
            aspirante.estado = estado
            self.repository.guardar_aspirante(aspirante)
            # Aquí dispararemos el Observer para notificar al estudiante
            return True
        return False
    def preparar_formulario_inscripcion(self):
        """Obtiene datos necesarios para la interfaz."""
        return {
            'periods': self.repository.obtener_periodos(),
            'careers': self.repository.obtener_carreras_activas()
        }

    def procesar_inscripcion(self, form_data: dict):
        """
        Caso de Uso principal que aplica los patrones de la Unidad 3.
        """
        # 1. CHAIN OF RESPONSIBILITY: Validación
        # Aquí puedes llamar a tu lógica de validación
        estudiantes = self.repository.listar_estudiantes_crudos()
        # (Supongamos que aquí ejecutas tu cadena de validación)
        
        # 2. CREACIÓN DE OBJETO (Unidad 1)
        try:
            nombre = f"{form_data.get('apellidos')} {form_data.get('nombres')}"
            nuevo = Aspirante(nombre=nombre, correo=form_data.get('correo'))
            
            # 3. GUARDADO (Inyección de Dependencias)
            self.repository.guardar_aspirante(nuevo)

            # 4. OBSERVER & BRIDGE: Notificaciones
            # Aquí es donde 'emites' el evento o envías el correo
            print(f"Notificando registro de: {nuevo.nombre}")
            
            return True, "Inscripción exitosa"
        except Exception as e:
            return False, str(e)