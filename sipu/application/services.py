from ..domain.models import Aspirante
from ..domain.interfaces import ISipuRepository
from fpdf import FPDF
import io

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
        # Obtenemos los aspirantes reales (excluyendo admin)
        todos = self.repository.listar_estudiantes_crudos()
        aspirantes = [u for u in todos if u.get('rol') != 'admin']
        
        # Creamos diccionarios de traducción ID -> Nombre
        per_map = {p['id']: p['nombre'] for p in self.repository.obtener_periodos()}
        car_map = {c['id']: c['nombre'] for c in self.repository.obtener_carreras()}
        
        for a in aspirantes:
            # Traducimos los IDs a nombres para la tabla
            a['dni_display'] = a.get('dni', 'Sin DNI')
            a['periodo_nombre'] = per_map.get(a.get('periodo'), 'No asignado')
            a['carrera_nombre'] = car_map.get(a.get('carrera'), 'No asignada')
            
        return aspirantes
    
    def autenticar_usuario(self, correo: str, contrasena: str):
        usuario_doc = self.repository.students.find_one({'correo': correo})
        
        if usuario_doc and usuario_doc.get('contrasena') == contrasena:
            if usuario_doc.get('rol') == 'admin':
                from ..domain.models import Administrador
                return Administrador(nombre=usuario_doc['nombre'], correo=usuario_doc['correo'])
            else:
                # REHIDRATAR CON CAMPOS COMPLETOS
                aspirante = Aspirante(
                    nombre=usuario_doc['nombre'], 
                    correo=usuario_doc['correo'],
                    dni=usuario_doc.get('dni'),
                    periodo=usuario_doc.get('periodo'),
                    carrera=usuario_doc.get('carrera')
                )
                aspirante.estado = usuario_doc.get('estado', 'Pendiente')
                return aspirante
        return None
    
    def generar_reporte_pdf(self, dni):
        # 1. Obtener objeto completo desde el repositorio corregido
        aspirante = self.repository.obtener_aspirante_por_dni(dni)
        if not aspirante:
            return None

        # 2. Mapas de traducción (ID -> Nombre real)
        # Esto busca en las colecciones de periodos y carreras
        per_map = {p['id']: p['nombre'] for p in self.repository.obtener_periodos()}
        car_map = {c['id']: c['nombre'] for c in self.repository.obtener_carreras()}

        # 3. Configuración del PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "COMPROBANTE DE INSCRIPCIÓN", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        # Usamos f-strings para insertar los datos del objeto
        pdf.cell(0, 10, f"Aspirante: {aspirante.nombre}", ln=True)
        pdf.cell(0, 10, f"Cédula/DNI: {aspirante.dni}", ln=True)
        
        # TRADUCCIÓN: Si el mapa no encuentra el ID, pone 'No asignado'
        carrera_nombre = car_map.get(aspirante.carrera, "Carrera no encontrada")
        periodo_nombre = per_map.get(aspirante.periodo, "Periodo no encontrado")
        
        pdf.cell(0, 10, f"Carrera: {carrera_nombre}", ln=True)
        pdf.cell(0, 10, f"Periodo: {periodo_nombre}", ln=True)
        pdf.cell(0, 10, f"Estado del Trámite: {aspirante.estado}", ln=True)

        # 4. Preparar buffer
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    
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

    def procesar_inscripcion(self, form_data: dict):
        try:
            # 1. Preparar el nombre completo
            nom = form_data.get('nombres', '').strip()
            ape = form_data.get('apellidos', '').strip()
            nombre_completo = f"{nom} {ape}".strip()
            
            # 2. Instanciar el objeto de dominio con los 5 campos clave
            nuevo_aspirante = Aspirante(
                nombre=nombre_completo,
                correo=form_data.get('correo'),
                dni=form_data.get('dni'),
                periodo=form_data.get('periodo'),
                carrera=form_data.get('carrera')
            )

            # 3. Pasar el objeto al repositorio
            self.repository.guardar_aspirante(nuevo_aspirante)
            
            return True, "Inscripción procesada correctamente"
            
        except Exception as e:
            print(f"Error: {e}") # Aquí es donde salía el error del setter
            return False, str(e)
    