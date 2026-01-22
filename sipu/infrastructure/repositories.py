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
        """Consulta la colección 'periods' usando el Singleton."""
        return list(self.db.periods.find({"activo": True}))

    def obtener_carreras(self):
        """Consulta la colección 'careers'."""
        return list(self.db.careers.find())
    def listar_estudiantes_crudos(self) -> list:
        """Retorna la lista de diccionarios directamente de Mongo para validaciones."""
        return list(self.students.find())

    def obtener_periodos(self):
        """Retorna los periodos para el formulario."""
        return list(self.db.periods.find())

    def obtener_carreras_activas(self):
        """Retorna las carreras para el formulario."""
        return list(self.db.careers.find({'active': True}))
    def obtener_aspirante_por_correo(self, correo: str) -> Optional[Aspirante]:
        doc = self.students.find_one({'correo': correo})
        if doc:
            # Rehidratamos el objeto con TODOS los campos de la DB
            aspirante = Aspirante(
                nombre=doc['nombre'], 
                correo=doc['correo'],
                dni=doc.get('dni'),
                periodo=doc.get('periodo'),
                carrera=doc.get('carrera')
            )
            aspirante.estado = doc.get('estado', 'Pendiente')
            return aspirante
        return None

    # Tu método guardar_aspirante ya estaba bien, 
    # pero asegúrate de que use las variables del objeto:
    def guardar_aspirante(self, aspirante: Aspirante) -> bool:
        student_doc = {
            'nombre': aspirante.nombre,  # Lee de la property
            'correo': aspirante.correo,  # Lee de la property
            'dni': aspirante.dni,
            'periodo': aspirante.periodo,
            'carrera': aspirante.carrera,
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
            # Si no los pasas aquí, el Service recibirá un objeto "vacío"
            aspirante = Aspirante(
                nombre=doc.get('nombre'),
                correo=doc.get('correo'),
                dni=doc.get('dni'),
                periodo=doc.get('periodo'), # VITAL: Traer el ID del periodo
                carrera=doc.get('carrera')   # VITAL: Traer el ID de la carrera
            )
            aspirante.estado = doc.get('estado', 'Pendiente')
            return aspirante
        return None

    def close(self):
        self.client.close()