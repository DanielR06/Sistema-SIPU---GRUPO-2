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
    
    # ========== MÉTODOS PARA EXÁMENES ==========
    
    def distribuir_aspirantes_en_examenes(self, examen_id: str) -> tuple:
        """
        Distribuye automáticamente aspirantes en laboratorios para un examen.
        Retorna (éxito: bool, mensaje: str)
        """
        try:
            # 1. Obtener datos del examen
            examen = self.repository.obtener_examen_por_id(examen_id)
            if not examen:
                return False, "Examen no encontrado"
            
            periodo = examen.get('periodo')
            carrera = examen.get('carrera')
            jornada = examen.get('jornada')
            
            # 2. Obtener aspirantes que pertenecen a este examen
            todos_aspirantes = self.repository.listar_estudiantes_crudos()
            aspirantes_examen = [
                a for a in todos_aspirantes 
                if a.get('estado') == 'Inscrito' and 
                   a.get('periodo') == periodo and 
                   a.get('carrera') == carrera and 
                   a.get('jornada') == jornada and 
                   a.get('rol') == 'aspirante'
            ]
            
            if not aspirantes_examen:
                return False, "No hay aspirantes para este examen"
            
            # 3. Obtener laboratorios disponibles
            laboratorios = self.repository.obtener_laboratorios()
            if not laboratorios:
                return False, "No hay laboratorios disponibles"
            
            # 4. Calcular distribución (usando round-robin)
            total_aspirantes = len(aspirantes_examen)
            total_capacidad = sum(lab['capacidad'] for lab in laboratorios)
            
            if total_capacidad < total_aspirantes:
                return False, f"Capacidad insuficiente: {total_aspirantes} aspirantes vs {total_capacidad} computadoras"
            
            # 5. Eliminar asignaciones anteriores si existen
            self.repository.eliminar_asignaciones_examen(examen_id)
            
            # 6. Crear asignaciones distribuidas
            lab_index = 0
            comp_numero = 1  # Número de computadora dentro del lab
            contador_asignaciones = 0
            
            for aspirante in aspirantes_examen:
                lab_actual = laboratorios[lab_index]
                
                asignacion = {
                    'id': f"asig_{examen_id}_{aspirante['correo']}",
                    'examen_id': examen_id,
                    'aspirante_correo': aspirante['correo'],
                    'aspirante_nombre': aspirante['nombre'],
                    'lab_id': lab_actual['id'],
                    'lab_nombre': lab_actual['nombre'],
                    'num_computadora': comp_numero,
                    'sede': lab_actual['sede'],
                    'estado': 'Pendiente'
                }
                
                self.repository.crear_asignacion_examen(asignacion)
                contador_asignaciones += 1
                
                # Avanzar a siguiente computadora
                comp_numero += 1
                
                # Si se alcanzó la capacidad del lab, pasar al siguiente
                if comp_numero > lab_actual['capacidad']:
                    comp_numero = 1
                    lab_index += 1
                    
                    # Si no hay más labs, reiniciar (distribuir en múltiples tandas)
                    if lab_index >= len(laboratorios):
                        lab_index = 0
            
            mensaje = f"✅ {contador_asignaciones} aspirantes distribuidos en {len(laboratorios)} laboratorios"
            return True, mensaje
        
        except Exception as e:
            print(f"Error en distribución: {e}")
            return False, f"Error: {str(e)}"
    
    def obtener_examen_aspirante(self, correo: str):
        """Obtiene el examen más reciente asignado a un aspirante con toda la información."""
        try:
            asignaciones = self.repository.obtener_asignaciones_por_aspirante(correo)
            
            if not asignaciones:
                return None
            
            # Tomar la asignación más reciente (la última creada)
            # O si hay múltiples, devolver la que tenga nota (ya calificada), sino la más reciente
            asignacion_con_nota = next((a for a in asignaciones if a.get('nota')), None)
            asignacion = asignacion_con_nota if asignacion_con_nota else asignaciones[-1]
            
            examen = self.repository.obtener_examen_por_id(asignacion['examen_id'])
            
            if examen:
                asignacion['examen_fecha'] = examen.get('fecha')
                asignacion['examen_hora_inicio'] = examen.get('hora_inicio')
                asignacion['examen_hora_fin'] = examen.get('hora_fin')
            
            return asignacion
        
        except Exception as e:
            print(f"Error al obtener examen: {e}")
            return None
    
    def guardar_calificacion_aspirante(self, asignacion_id: str, presentó: bool, nota: int, observaciones: str) -> tuple:
        """Guarda la calificación de un aspirante. Retorna (éxito, mensaje)."""
        try:
            if presentó:
                if not (1 <= nota <= 1000):
                    return False, "La nota debe estar entre 1 y 1000"
            
            exito = self.repository.guardar_calificacion(asignacion_id, presentó, nota, observaciones)
            
            if exito:
                return True, "Calificación guardada correctamente"
            else:
                return False, "Error al guardar la calificación"
        
        except Exception as e:
            return False, str(e)
    
    def obtener_calificaciones_aspirante(self, correo: str):
        """Obtiene todas las calificaciones de un aspirante con información del examen."""
        try:
            calificaciones = self.repository.obtener_calificaciones_aspirante(correo)
            
            # Enriquecer con información del examen
            for cal in calificaciones:
                examen = self.repository.obtener_examen_por_id(cal.get('examen_id'))
                if examen:
                    periodos = {p['id']: p['nombre'] for p in self.repository.obtener_periodos()}
                    carreras = {c['id']: c['nombre'] for c in self.repository.obtener_carreras()}
                    
                    cal['examen_periodo'] = periodos.get(examen.get('periodo'), 'N/A')
                    cal['examen_carrera'] = carreras.get(examen.get('carrera'), 'N/A')
                    cal['examen_jornada'] = examen.get('jornada')
                    cal['examen_fecha'] = examen.get('fecha')
            
            return calificaciones
        
        except Exception as e:
            print(f"Error al obtener calificaciones: {e}")
            return []
    
