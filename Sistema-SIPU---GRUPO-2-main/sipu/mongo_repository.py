"""Repositorio MongoDB para SIPU."""
import os
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId


class MongoDBRepository:
    """Repositorio usando MongoDB para estudiantes, periodos, carreras y documentos."""
    
    def __init__(self, connection_string: str = None, database_name: str = "sipu_db"):
        """
        Inicializa la conexión a MongoDB.
        
        Args:
            connection_string: URI de conexión a MongoDB (por defecto: localhost)
            database_name: Nombre de la base de datos
        """
        if connection_string is None:
            connection_string = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        
        # Colecciones
        self.students = self.db.students
        self.periods = self.db.periods
        self.careers = self.db.careers
        self.documents = self.db.documents
        
        # Crear índices
        self._create_indexes()
        # Insertar datos por defecto
        self._initialize_default_data()
    
    def _create_indexes(self):
        """Crea índices únicos para optimizar búsquedas."""
        # Índice único en correo de estudiantes
        self.students.create_index("correo", unique=True)
        # Índices para búsquedas comunes
        self.periods.create_index("active")
        self.careers.create_index("active")
        self.documents.create_index("student_id")
    
    def _initialize_default_data(self):
        """Inserta carreras por defecto si no existen."""
        if self.careers.count_documents({}) == 0:
            default_careers = [
                {'name': 'Ingeniería de Sistemas', 'active': True},
                {'name': 'Ingeniería Civil', 'active': True},
                {'name': 'Ingeniería Industrial', 'active': True},
                {'name': 'Administración', 'active': True},
                {'name': 'Contabilidad', 'active': True},
                {'name': 'Derecho', 'active': True},
                {'name': 'Medicina', 'active': True},
                {'name': 'Enfermería', 'active': True}
            ]
            self.careers.insert_many(default_careers)
    
    def _row_to_dict(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte un documento MongoDB a un diccionario compatible con el formato anterior."""
        if doc is None:
            return None
        result = dict(doc)
        if '_id' in result:
            result['id'] = str(result['_id'])
            del result['_id']
        return result
    
    # ========== STUDENTS ==========
    
    def add_student(self, nombre: str, correo: str, dni: Optional[str] = None, 
                   period_id: Optional[str] = None, inscripcion_finalizada: int = 0, 
                   apellidos: Optional[str] = None, nombres: Optional[str] = None, 
                   career_id: Optional[str] = None) -> str:
        """Agrega un nuevo estudiante."""
        full_name = nombre
        if (not full_name or full_name.strip() == "") and (apellidos or nombres):
            full_name = f"{(apellidos or '').strip()} {(nombres or '').strip()}".strip()
        
        student_doc = {
            'nombre': full_name,
            'apellidos': apellidos,
            'nombres': nombres,
            'correo': correo,
            'dni': dni,
            'period_id': period_id,
            'career_id': career_id,
            'inscripcion_finalizada': inscripcion_finalizada
        }
        
        try:
            result = self.students.insert_one(student_doc)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError(f"El correo '{correo}' ya está registrado")
    
    def list_students(self) -> List[Dict[str, Any]]:
        """Lista todos los estudiantes con información de período y carrera."""
        pipeline = [
            {
                '$lookup': {
                    'from': 'periods',
                    'let': {'period_id': {'$toObjectId': '$period_id'}},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$period_id']}}}
                    ],
                    'as': 'period'
                }
            },
            {
                '$lookup': {
                    'from': 'careers',
                    'let': {'career_id': {'$toObjectId': '$career_id'}},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$career_id']}}}
                    ],
                    'as': 'career'
                }
            },
            {
                '$addFields': {
                    'period_name': {'$arrayElemAt': ['$period.name', 0]},
                    'career_name': {'$arrayElemAt': ['$career.name', 0]}
                }
            },
            {'$sort': {'_id': -1}}
        ]
        
        results = list(self.students.aggregate(pipeline))
        return [self._row_to_dict(r) for r in results]
    
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un estudiante por ID."""
        try:
            doc = self.students.find_one({'_id': ObjectId(student_id)})
            return self._row_to_dict(doc)
        except Exception:
            return None
    
    # ========== PERIODS ==========
    
    def add_period(self, name: str, active: int = 0, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> str:
        """Agrega un nuevo período."""
        period_doc = {
            'name': name,
            'active': bool(active),
            'start_date': start_date,
            'end_date': end_date
        }
        result = self.periods.insert_one(period_doc)
        return str(result.inserted_id)
    
    def list_periods(self) -> List[Dict[str, Any]]:
        """Lista todos los períodos."""
        results = list(self.periods.find().sort('_id', -1))
        return [self._row_to_dict(r) for r in results]
    
    def list_active_periods(self) -> List[Dict[str, Any]]:
        """Lista períodos activos."""
        results = list(self.periods.find({'active': True}).sort('_id', -1))
        return [self._row_to_dict(r) for r in results]
    
    def get_period(self, period_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un período por ID."""
        try:
            doc = self.periods.find_one({'_id': ObjectId(period_id)})
            return self._row_to_dict(doc)
        except Exception:
            return None
    
    # ========== CAREERS ==========
    
    def add_career(self, name: str, active: int = 1) -> str:
        """Agrega una nueva carrera."""
        career_doc = {
            'name': name,
            'active': bool(active)
        }
        result = self.careers.insert_one(career_doc)
        return str(result.inserted_id)
    
    def list_careers(self) -> List[Dict[str, Any]]:
        """Lista todas las carreras."""
        results = list(self.careers.find().sort('name', 1))
        return [self._row_to_dict(r) for r in results]
    
    def list_active_careers(self) -> List[Dict[str, Any]]:
        """Lista carreras activas."""
        results = list(self.careers.find({'active': True}).sort('name', 1))
        return [self._row_to_dict(r) for r in results]
    
    def get_career(self, career_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una carrera por ID."""
        try:
            doc = self.careers.find_one({'_id': ObjectId(career_id)})
            return self._row_to_dict(doc)
        except Exception:
            return None
    
    # ========== DOCUMENTS ==========
    
    def add_document(self, student_id: str, tipo: str, ruta: Optional[str] = None) -> str:
        """Agrega un nuevo documento."""
        doc = {
            'student_id': student_id,
            'tipo': tipo,
            'ruta': ruta
        }
        result = self.documents.insert_one(doc)
        return str(result.inserted_id)
    
    def list_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista documentos, opcionalmente filtrados por estudiante."""
        query = {'student_id': student_id} if student_id else {}
        results = list(self.documents.find(query).sort('_id', -1))
        return [self._row_to_dict(r) for r in results]
    
    def close(self):
        """Cierra la conexión a MongoDB."""
        try:
            self.client.close()
        except Exception:
            pass
