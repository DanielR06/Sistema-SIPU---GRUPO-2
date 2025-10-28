import sqlite3
from typing import List, Tuple, Optional

class SQLiteRepository:
    """Repositorio sencillo usando sqlite3 para estudiantes y documentos."""
    def __init__(self, db_path: str = "sipu.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self._conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            dni TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            ruta TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
        """)
        self._conn.commit()

        # Tabla para periodos 
        cur.execute("""
        CREATE TABLE IF NOT EXISTS periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 0,
            start_date TEXT,
            end_date TEXT
        )
        """)
        self._conn.commit()
        # Ensure students table has period_id and inscripcion_finalizada columns (ALTER if needed)
        cur.execute("PRAGMA table_info(students)")
        cols = [r[1] for r in cur.fetchall()]
        if 'apellidos' not in cols:
            try:
                cur.execute("ALTER TABLE students ADD COLUMN apellidos TEXT")
            except Exception:
                pass
        if 'nombres' not in cols:
            try:
                cur.execute("ALTER TABLE students ADD COLUMN nombres TEXT")
            except Exception:
                pass
        if 'period_id' not in cols:
            try:
                cur.execute("ALTER TABLE students ADD COLUMN period_id INTEGER")
            except Exception:
                pass
        if 'inscripcion_finalizada' not in cols:
            try:
                cur.execute("ALTER TABLE students ADD COLUMN inscripcion_finalizada INTEGER DEFAULT 0")
            except Exception:
                pass
        self._conn.commit()

    # Estudiantes
    def add_student(self, nombre: str, correo: str, dni: Optional[str] = None, period_id: Optional[int] = None, inscripcion_finalizada: int = 0, apellidos: Optional[str] = None, nombres: Optional[str] = None) -> int:
        cur = self._conn.cursor()
        # si se pasaron apellidos/nombres, construir el nombre completo
        full_name = nombre
        if (not full_name or full_name.strip() == "") and (apellidos or nombres):
            full_name = f"{(apellidos or '').strip()} {(nombres or '').strip()}".strip()
        try:
            cur.execute("INSERT INTO students (nombre, apellidos, nombres, correo, dni, period_id, inscripcion_finalizada) VALUES (?, ?, ?, ?, ?, ?, ?)", (full_name, apellidos, nombres, correo, dni, period_id, inscripcion_finalizada))
            self._conn.commit()
            return int(cur.lastrowid or 0)
        except sqlite3.IntegrityError as e:
            raise ValueError(f"No se pudo insertar estudiante: {e}")

    # Periodos
    def add_period(self, name: str, active: int = 0, start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
        cur = self._conn.cursor()
        cur.execute("INSERT INTO periods (name, active, start_date, end_date) VALUES (?, ?, ?, ?)", (name, active, start_date, end_date))
        self._conn.commit()
        return int(cur.lastrowid or 0)

    def list_periods(self) -> List[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, name, active, start_date, end_date FROM periods ORDER BY id DESC")
        return cur.fetchall()

    def list_active_periods(self) -> List[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, name, active, start_date, end_date FROM periods WHERE active = 1 ORDER BY id DESC")
        return cur.fetchall()

    def get_period(self, period_id: int) -> Optional[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, name, active, start_date, end_date FROM periods WHERE id = ?", (period_id,))
        return cur.fetchone()

    def list_students(self) -> List[sqlite3.Row]:
        cur = self._conn.cursor()
        # join with periods to include period name if available and the inscripcion flag
        cur.execute("""
        SELECT s.id, s.nombre, s.apellidos, s.nombres, s.correo, s.dni, s.period_id, s.inscripcion_finalizada,
               p.name as period_name
        FROM students s
        LEFT JOIN periods p ON s.period_id = p.id
        ORDER BY s.id DESC
        """)
        return cur.fetchall()

    def get_student(self, student_id: int) -> Optional[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, nombre, correo, dni, period_id, inscripcion_finalizada FROM students WHERE id = ?", (student_id,))
        return cur.fetchone()

    # Documentos
    def add_document(self, student_id: int, tipo: str, ruta: Optional[str] = None) -> int:
        cur = self._conn.cursor()
        cur.execute("INSERT INTO documents (student_id, tipo, ruta) VALUES (?, ?, ?)", (student_id, tipo, ruta))
        self._conn.commit()
        return int(cur.lastrowid or 0)

    def list_documents(self, student_id: Optional[int] = None) -> List[sqlite3.Row]:
        cur = self._conn.cursor()
        if student_id is None:
            cur.execute("SELECT id, student_id, tipo, ruta FROM documents ORDER BY id DESC")
        else:
            cur.execute("SELECT id, student_id, tipo, ruta FROM documents WHERE student_id = ? ORDER BY id DESC", (student_id,))
        return cur.fetchall()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
