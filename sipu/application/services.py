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
    
    # application/services.py

    def generar_reporte_pdf(self, correo_usuario):
        # 1. LEER DIRECTO: Obtenemos el diccionario (no el objeto)
        aspirante_dict = self.repository.obtener_aspirante_crudo_por_correo(correo_usuario)
        
        if not aspirante_dict:
            return None

        # 2. TRADUCCIÓN: Seguimos necesitando los nombres reales
        per_map = {p['id']: p['nombre'] for p in self.repository.obtener_periodos()}
        car_map = {c['id']: c['nombre'] for c in self.repository.obtener_carreras()}

        # 3. CONSTRUCCIÓN DEL PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "REPORTE DE INSCRIPCIÓN OFICIAL", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        
        # IMPORTANTE: Ahora usamos ['llave'] porque es un diccionario
        pdf.cell(0, 10, f"Nombre: {aspirante_dict.get('nombre', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Correo: {aspirante_dict.get('correo', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"DNI: {aspirante_dict.get('dni', 'S/N')}", ln=True)
        
        # Buscamos en los mapas usando las llaves del diccionario
        id_periodo = aspirante_dict.get('periodo')
        id_carrera = aspirante_dict.get('carrera')
        
        pdf.cell(0, 10, f"Período: {per_map.get(id_periodo, 'No encontrado')}", ln=True)
        pdf.cell(0, 10, f"Carrera: {car_map.get(id_carrera, 'No encontrada')}", ln=True)
        pdf.cell(0, 10, f"Estado: {aspirante_dict.get('estado', 'Pendiente')}", ln=True)

        # 4. Retornar el buffer
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
    