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
    def guardar_aspirante(self, aspirante: Aspirante) -> bool:
        
        """
        Convierte un objeto Aspirante (Dominio) a formato Mongo (Infraestructura).
        """
        student_doc = {
            'nombre': aspirante.nombre,
            'correo': aspirante.correo,
            'estado': aspirante.estado
        }
        
        # Usamos update_one con upsert para guardar o actualizar
        result = self.students.update_one(
            {'correo': aspirante.correo},
            {'$set': student_doc},
            upsert=True
        )
        return result.acknowledged

    def obtener_aspirante_por_correo(self, correo: str) -> Optional[Aspirante]:
        """
        Busca en Mongo y devuelve un Objeto Aspirante (Unidad 1: Objetos).
        """
        doc = self.students.find_one({'correo': correo})
        if doc:
            # Rehidratamos el objeto de dominio desde los datos de la DB
            aspirante = Aspirante(nombre=doc['nombre'], correo=doc['correo'])
            aspirante.estado = doc.get('estado', 'Pendiente')
            return aspirante
        return None

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

    def close(self):
        self.client.close()