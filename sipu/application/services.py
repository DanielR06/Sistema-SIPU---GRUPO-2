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
        aspirante = self.repository.obtener_aspirante_por_correo(correo_usuario)
        if not aspirante: return None

        # Mapas de traducción: Usan el campo 'id' (no _id) para coincidir con lo guardado en estudiantes
        per_map = {p.get('id'): p.get('nombre') for p in self.repository.obtener_periodos()}
        car_map = {c.get('id'): c.get('nombre') for c in self.repository.obtener_carreras()}

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "REPORTE DE INSCRIPCIÓN", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Nombre: {aspirante.nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {aspirante.dni}", ln=True)
        
        # TRADUCCIÓN: Buscamos el nombre real usando el ID que tiene el objeto
        periodo_real = per_map.get(aspirante.periodo, aspirante.periodo or "No asignado")
        carrera_real = car_map.get(aspirante.carrera, aspirante.carrera or "No asignada")
        
        pdf.cell(0, 10, f"Período: {periodo_real}", ln=True)
        pdf.cell(0, 10, f"Carrera: {carrera_real}", ln=True)

        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    
    def generar_reporte_pdf_por_dni(self, dni: str):
        """Genera PDF buscando por DNI en lugar de correo."""
        aspirante = self.repository.obtener_aspirante_por_dni(dni)
        if not aspirante: 
            return None

        # Mapas de traducción: Usan el campo 'id' para coincidir con lo guardado en estudiantes
        periodos = self.repository.obtener_periodos()
        carreras = self.repository.obtener_carreras()
        sedes = self.repository.obtener_sedes()
        
        # Crear mapas usando 'id' (no _id)
        per_map = {p.get('id'): p.get('nombre') for p in periodos}
        car_map = {c.get('id'): c.get('nombre') for c in carreras}
        sed_map = {s.get('id'): s.get('nombre') for s in sedes}

        # TRADUCCIÓN: Buscamos los nombres reales usando los IDs
        periodo_real = per_map.get(aspirante.periodo, aspirante.periodo or "No asignado")
        carrera_real = car_map.get(aspirante.carrera, aspirante.carrera or "No asignada")
        sede_real = sed_map.get(aspirante.sede, aspirante.sede or "No asignada")

        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "REPORTE DE INSCRIPCIÓN", ln=True, align='C')
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, "Sistema de Inscripción SIPU", ln=True, align='C')
        pdf.ln(5)
        
        # Línea separadora
        pdf.set_draw_color(100, 100, 100)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Tabla de Información del Aspirante
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "INFORMACIÓN DEL ASPIRANTE", ln=True)
        pdf.ln(2)
        
        # Tabla 1: Datos del aspirante
        pdf.set_font("Arial", "", 10)
        pdf.set_fill_color(200, 200, 200)
        
        # Encabezados
        pdf.cell(50, 8, "Campo", border=1, fill=True, align='C')
        pdf.cell(0, 8, "Valor", border=1, fill=True, ln=True, align='L')
        
        # Datos
        pdf.set_fill_color(240, 240, 240)
        data_aspirante = [
            ("Nombre", aspirante.nombre),
            ("Correo", aspirante.correo),
            ("DNI/Cédula", aspirante.dni),
        ]
        
        fill = False
        for label, valor in data_aspirante:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(50, 8, label, border=1, fill=fill)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, str(valor), border=1, fill=fill, ln=True)
            fill = not fill
        
        pdf.ln(5)
        
        # Línea separadora
        pdf.set_draw_color(100, 100, 100)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Tabla 2: Información de Inscripción
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "INFORMACIÓN DE INSCRIPCIÓN", ln=True)
        pdf.ln(2)
        
        pdf.set_font("Arial", "", 10)
        pdf.set_fill_color(200, 200, 200)
        
        # Encabezados
        pdf.cell(50, 8, "Campo", border=1, fill=True, align='C')
        pdf.cell(0, 8, "Valor", border=1, fill=True, ln=True, align='L')
        
        # Datos
        pdf.set_fill_color(240, 240, 240)
        data_inscripcion = [
            ("Período", periodo_real),
            ("Carrera", carrera_real),
            ("Jornada", aspirante.jornada or "No asignada"),
            ("Sede", sede_real),
        ]
        
        fill = False
        for label, valor in data_inscripcion:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(50, 8, label, border=1, fill=fill)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, str(valor), border=1, fill=fill, ln=True)
            fill = not fill
        
        pdf.ln(10)
        
        # Línea separadora
        pdf.set_draw_color(100, 100, 100)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Pie de página
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 8, f"Documento generado automáticamente | Fecha: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')

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
            # Obtener datos del formulario
            correo = form_data.get('correo', '').strip()
            dni = form_data.get('dni', '').strip()
            periodo = form_data.get('periodo', '').strip()
            carrera = form_data.get('carrera', '').strip()
            jornada = form_data.get('jornada', '').strip()
            sede = form_data.get('sede', '').strip()
            
            if not correo or not dni or not periodo or not carrera or not jornada or not sede:
                return False, "Todos los campos son obligatorios"
            
            # Buscar el aspirante existente
            aspirante = self.repository.obtener_aspirante_por_correo(correo)
            if not aspirante:
                return False, "Aspirante no encontrado"
            
            # Actualizar con los datos de inscripción
            aspirante.dni = dni
            aspirante.periodo = periodo
            aspirante.carrera = carrera
            aspirante.jornada = jornada
            aspirante.sede = sede
            aspirante.estado = 'Inscrito'

            # Guardar cambios
            self.repository.guardar_aspirante(aspirante)
            
            return True, "Inscripción procesada correctamente"
            
        except Exception as e:
            print(f"Error: {e}")
            return False, str(e)
    