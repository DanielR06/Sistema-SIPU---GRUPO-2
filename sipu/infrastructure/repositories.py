import os
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId

# Importamos la interfaz y los modelos para cumplir con la Unidad 2 (DIP)
from ..domain.interfaces import ISipuRepository
from ..domain.models import Aspirante, Documento
from .database import MongoDBClient # Importamos el Singleton

class MongoSipuRepository(ISipuRepository):
    def __init__(self):
        # En lugar de crear un cliente nuevo, pedimos la instancia Singleton
        self.mongo_manager = MongoDBClient()
        self.db = self.mongo_manager.database
        
        # Colecciones
        self.students = self.db.students
        self.documents = self.db.documents

    # --- Implementación de la Interfaz ---
    def obtener_periodos(self):
        """Retorna todos los periodos disponibles."""
        return list(self.db.periods.find())

    def obtener_carreras(self):
        """Retorna todas las carreras disponibles."""
        return list(self.db.careers.find())
    
    def obtener_sedes(self):
        """Retorna todas las sedes disponibles."""
        return list(self.db.sedes.find())
    
    def listar_estudiantes_crudos(self) -> list:
        """Retorna la lista de diccionarios directamente de Mongo para validaciones."""
        return list(self.students.find())
    def obtener_aspirante_por_correo(self, correo: str) -> Optional[Aspirante]:
        doc = self.students.find_one({'correo': correo})
        if doc:
            # IMPORTANTE: Rehidratamos el objeto con TODOS los campos de la DB
            return Aspirante(
                nombre=doc.get('nombre'),
                correo=doc.get('correo'),
                dni=doc.get('dni'),
                periodo=doc.get('periodo'),
                carrera=doc.get('carrera'),
                jornada=doc.get('jornada'),
                sede=doc.get('sede')
            )
        return None

    # 2. El que usaremos para el "Camino Directo" del PDF
    def obtener_aspirante_crudo_por_correo(self, correo: str):
        """Retorna el diccionario directo de MongoDB sin validaciones de clase."""
        return self.students.find_one({'correo': correo})
    # Tu método guardar_aspirante ya estaba bien, 
    # pero asegúrate de que use las variables del objeto:
    def guardar_aspirante(self, aspirante: Aspirante) -> bool:
        student_doc = {
            'nombre': aspirante.nombre,  # Lee de la property
            'correo': aspirante.correo,  # Lee de la property
            'dni': aspirante.dni,
            'periodo': aspirante.periodo,
            'carrera': aspirante.carrera,
            'jornada': aspirante.jornada,
            'sede': aspirante.sede,
            'rol': 'aspirante',
            'estado': aspirante.estado
        }
        result = self.students.update_one(
            {'correo': aspirante.correo},
            {'$set': student_doc},
            upsert=True
        )
        return result.acknowledged
    def listar_documentos(self, propietario_id: str) -> List[Documento]:
        """
        Devuelve una lista de objetos Documento (Unidad 1: Relaciones).
        """
        cursor = self.documents.find({'student_id': propietario_id})
        documentos_obj = []
        
        for doc in cursor:
            # Convertimos cada registro de Mongo en un Objeto del Dominio
            obj = Documento(
                tipo=doc['tipo'],
                nombre_archivo=doc.get('nombre_archivo', 'archivo_sin_nombre'),
                propietario=propietario_id
            )
            obj.revisar_documento(doc.get('estado', 'Pendiente'), doc.get('obs', ''))
            documentos_obj.append(obj)
            
        return documentos_obj
    def obtener_aspirante_por_dni(self, dni: str) -> Optional[Aspirante]:
        # 1. Buscamos el documento en MongoDB
        doc = self.students.find_one({'dni': dni})
        
        if doc:
            # 2. REHIDRATACIÓN: Creamos el objeto con TODOS los campos
            aspirante = Aspirante(
                nombre=doc.get('nombre'),
                correo=doc.get('correo'),
                dni=doc.get('dni'),
                periodo=doc.get('periodo'),
                carrera=doc.get('carrera'),
                jornada=doc.get('jornada'),
                sede=doc.get('sede')
            )
            aspirante.estado = doc.get('estado', 'Pendiente')
            return aspirante
        return None

    def close(self):
        self.client.close()
    
    # ========== MÉTODOS PARA EXÁMENES ==========
    
    def obtener_laboratorios(self):
        """Retorna todos los laboratorios disponibles."""
        return list(self.db.laboratories.find())
    
    def obtener_laboratorios_por_sede(self, sede: str):
        """Retorna los laboratorios de una sede específica."""
        return list(self.db.laboratories.find({'sede': sede}))
    
    def crear_examen(self, examen_dict: dict) -> bool:
        """Crea un nuevo examen."""
        try:
            self.db.examenes.insert_one(examen_dict)
            return True
        except Exception as e:
            print(f"Error al crear examen: {e}")
            return False
    
    def obtener_examenes(self):
        """Retorna todos los exámenes."""
        return list(self.db.examenes.find())
    
    def obtener_examenes_por_periodo_carrera_jornada(self, periodo: str, carrera: str, jornada: str):
        """Obtiene exámenes para una combinación específica."""
        return list(self.db.examenes.find({
            'periodo': periodo,
            'carrera': carrera,
            'jornada': jornada
        }))
    
    def obtener_examen_por_id(self, examen_id: str):
        """Obtiene un examen específico por su ID."""
        return self.db.examenes.find_one({'id': examen_id})
    
    def crear_asignacion_examen(self, asignacion_dict: dict) -> bool:
        """Crea una asignación de aspirante a examen."""
        try:
            self.db.asignaciones_examen.insert_one(asignacion_dict)
            return True
        except Exception as e:
            print(f"Error al crear asignación: {e}")
            return False
    
    def obtener_asignaciones_por_examen(self, examen_id: str):
        """Obtiene todas las asignaciones para un examen."""
        return list(self.db.asignaciones_examen.find({'examen_id': examen_id}))
    
    def obtener_asignaciones_por_aspirante(self, correo: str):
        """Obtiene los exámenes asignados a un aspirante."""
        return list(self.db.asignaciones_examen.find({'aspirante_correo': correo}))
    
    def contar_asignaciones_por_lab(self, lab_id: str, examen_id: str) -> int:
        """Cuenta cuántas personas están asignadas a un laboratorio en un examen."""
        return self.db.asignaciones_examen.count_documents({
            'lab_id': lab_id,
            'examen_id': examen_id
        })
    
    def eliminar_asignaciones_examen(self, examen_id: str) -> bool:
        """Elimina todas las asignaciones de un examen (para regenerar)."""
        try:
            self.db.asignaciones_examen.delete_many({'examen_id': examen_id})
            return True
        except Exception as e:
            print(f"Error al eliminar asignaciones: {e}")
            return False