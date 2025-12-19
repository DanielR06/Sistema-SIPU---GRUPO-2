"""
Implementación del patrón de diseño Bridge para el sistema SIPU.
El patrón Bridge separa la abstracción de su implementación, permitiendo que varíen independientemente.
En este caso, separamos la lógica de repositorio (abstracción) de la implementación de base de datos (implementación).
"""

import sys
import os

# Agregar el directorio raíz al path para importaciones absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


# ========== IMPLEMENTOR (Implementación) ==========

class DatabaseImplementor(ABC):
    """Interfaz para las implementaciones de base de datos."""

    @abstractmethod
    def add_student(self, nombre: str, correo: str, dni: Optional[str] = None,
                   period_id: Optional[str] = None, inscripcion_finalizada: int = 0,
                   apellidos: Optional[str] = None, nombres: Optional[str] = None,
                   career_id: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def list_students(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_period(self, name: str, active: int = 0, start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def list_periods(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_active_periods(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_period(self, period_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_career(self, name: str, active: int = 1) -> str:
        pass

    @abstractmethod
    def list_careers(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_active_careers(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_career(self, career_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_document(self, student_id: str, tipo: str, ruta: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def list_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def close(self):
        pass


# ========== CONCRETE IMPLEMENTORS ==========

class MongoDBImplementor(DatabaseImplementor):
    """Implementación concreta usando MongoDB."""

    def __init__(self):
        from sipu.mongo_repository import MongoDBRepository
        self.repo = MongoDBRepository()

    def add_student(self, nombre: str, correo: str, dni: Optional[str] = None,
                   period_id: Optional[str] = None, inscripcion_finalizada: int = 0,
                   apellidos: Optional[str] = None, nombres: Optional[str] = None,
                   career_id: Optional[str] = None) -> str:
        return self.repo.add_student(nombre, correo, dni, period_id, inscripcion_finalizada, apellidos, nombres, career_id)

    def list_students(self) -> List[Dict[str, Any]]:
        return self.repo.list_students()

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_student(student_id)

    def add_period(self, name: str, active: int = 0, start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> str:
        return self.repo.add_period(name, active, start_date, end_date)

    def list_periods(self) -> List[Dict[str, Any]]:
        return self.repo.list_periods()

    def list_active_periods(self) -> List[Dict[str, Any]]:
        return self.repo.list_active_periods()

    def get_period(self, period_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_period(period_id)

    def add_career(self, name: str, active: int = 1) -> str:
        return self.repo.add_career(name, active)

    def list_careers(self) -> List[Dict[str, Any]]:
        return self.repo.list_careers()

    def list_active_careers(self) -> List[Dict[str, Any]]:
        return self.repo.list_active_careers()

    def get_career(self, career_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_career(career_id)

    def add_document(self, student_id: str, tipo: str, ruta: Optional[str] = None) -> str:
        return self.repo.add_document(student_id, tipo, ruta)

    def list_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.repo.list_documents(student_id)

    def close(self):
        self.repo.close()


class SQLiteImplementor(DatabaseImplementor):
    """Implementación concreta usando SQLite."""

    def __init__(self):
        from sipu.repository import SQLiteRepository
        self.repo = SQLiteRepository()

    def add_student(self, nombre: str, correo: str, dni: Optional[str] = None,
                   period_id: Optional[str] = None, inscripcion_finalizada: int = 0,
                   apellidos: Optional[str] = None, nombres: Optional[str] = None,
                   career_id: Optional[str] = None) -> str:
        # SQLite usa int para IDs, pero convertimos a str para consistencia
        student_id = self.repo.add_student(nombre, correo, dni, int(period_id) if period_id else None, inscripcion_finalizada, apellidos, nombres)
        return str(student_id)

    def list_students(self) -> List[Dict[str, Any]]:
        rows = self.repo.list_students()
        return [dict(row) for row in rows]

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        row = self.repo.get_student(int(student_id))
        return dict(row) if row else None

    def add_period(self, name: str, active: int = 0, start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> str:
        period_id = self.repo.add_period(name, active, start_date, end_date)
        return str(period_id)

    def list_periods(self) -> List[Dict[str, Any]]:
        rows = self.repo.list_periods()
        return [dict(row) for row in rows]

    def list_active_periods(self) -> List[Dict[str, Any]]:
        rows = self.repo.list_active_periods()
        return [dict(row) for row in rows]

    def get_period(self, period_id: str) -> Optional[Dict[str, Any]]:
        row = self.repo.get_period(int(period_id))
        return dict(row) if row else None

    def add_career(self, name: str, active: int = 1) -> str:
        # SQLite no tiene carreras por defecto, pero podemos agregar una tabla o simular
        # Para simplicidad, retornamos un ID dummy
        return "1"  # Placeholder

    def list_careers(self) -> List[Dict[str, Any]]:
        # Placeholder
        return []

    def list_active_careers(self) -> List[Dict[str, Any]]:
        # Placeholder
        return []

    def get_career(self, career_id: str) -> Optional[Dict[str, Any]]:
        # Placeholder
        return None

    def add_document(self, student_id: str, tipo: str, ruta: Optional[str] = None) -> str:
        doc_id = self.repo.add_document(int(student_id), tipo, ruta)
        return str(doc_id)

    def list_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = self.repo.list_documents(int(student_id) if student_id else None)
        return [dict(row) for row in rows]

    def close(self):
        self.repo.close()


# ========== ABSTRACTION (Abstracción) ==========

class Repository(ABC):
    """Abstracción que usa el implementor."""

    def __init__(self, implementor: DatabaseImplementor):
        self._implementor = implementor

    def set_implementor(self, implementor: DatabaseImplementor):
        """Permite cambiar la implementación en runtime."""
        self._implementor = implementor

    # Delegar métodos al implementor
    def add_student(self, nombre: str, correo: str, dni: Optional[str] = None,
                   period_id: Optional[str] = None, inscripcion_finalizada: int = 0,
                   apellidos: Optional[str] = None, nombres: Optional[str] = None,
                   career_id: Optional[str] = None) -> str:
        return self._implementor.add_student(nombre, correo, dni, period_id, inscripcion_finalizada, apellidos, nombres, career_id)

    def list_students(self) -> List[Dict[str, Any]]:
        return self._implementor.list_students()

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        return self._implementor.get_student(student_id)

    def add_period(self, name: str, active: int = 0, start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> str:
        return self._implementor.add_period(name, active, start_date, end_date)

    def list_periods(self) -> List[Dict[str, Any]]:
        return self._implementor.list_periods()

    def list_active_periods(self) -> List[Dict[str, Any]]:
        return self._implementor.list_active_periods()

    def get_period(self, period_id: str) -> Optional[Dict[str, Any]]:
        return self._implementor.get_period(period_id)

    def add_career(self, name: str, active: int = 1) -> str:
        return self._implementor.add_career(name, active)

    def list_careers(self) -> List[Dict[str, Any]]:
        return self._implementor.list_careers()

    def list_active_careers(self) -> List[Dict[str, Any]]:
        return self._implementor.list_active_careers()

    def get_career(self, career_id: str) -> Optional[Dict[str, Any]]:
        return self._implementor.get_career(career_id)

    def add_document(self, student_id: str, tipo: str, ruta: Optional[str] = None) -> str:
        return self._implementor.add_document(student_id, tipo, ruta)

    def list_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._implementor.list_documents(student_id)

    def close(self):
        self._implementor.close()


# ========== REFINED ABSTRACTIONS (Abstracciones refinadas) ==========

class SIPURepository(Repository):
    """Repositorio refinado para SIPU con funcionalidades adicionales."""

    def __init__(self, implementor: DatabaseImplementor):
        super().__init__(implementor)

    def get_students_by_period(self, period_id: str) -> List[Dict[str, Any]]:
        """Obtiene estudiantes filtrados por período."""
        students = self.list_students()
        return [s for s in students if s.get('period_id') == period_id]

    def get_students_by_career(self, career_id: str) -> List[Dict[str, Any]]:
        """Obtiene estudiantes filtrados por carrera."""
        students = self.list_students()
        return [s for s in students if s.get('career_id') == career_id]

    def count_students(self) -> int:
        """Cuenta el total de estudiantes."""
        return len(self.list_students())

    def count_periods(self) -> int:
        """Cuenta el total de períodos."""
        return len(self.list_periods())


# ========== FACTORY PARA CREAR EL REPOSITORIO ==========

def create_repository(use_mongodb: bool = True) -> SIPURepository:
    """Factory para crear el repositorio con la implementación apropiada."""
    if use_mongodb:
        implementor = MongoDBImplementor()
    else:
        implementor = SQLiteImplementor()
    return SIPURepository(implementor)
