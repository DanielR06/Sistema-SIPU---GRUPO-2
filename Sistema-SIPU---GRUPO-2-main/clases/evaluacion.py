"""Módulo de evaluación académica.

Contiene la clase Evaluacion con encapsulamiento de nota.
"""


class Evaluacion:
    """Clase para representar una evaluación académica."""
    
    def __init__(self, nota: float, tiempo_evaluacion: int):
        """
        Inicializa una evaluación.
        
        Args:
            nota: Nota obtenida (0-20)
            tiempo_evaluacion: Tiempo en minutos
        """
        self.__nota = nota
        self.tiempo_evaluacion = tiempo_evaluacion

    @property
    def nota(self) -> float:
        """Getter con encapsulamiento (decorador @property)."""
        return self.__nota

    @nota.setter
    def nota(self, valor: float):
        """
        Setter que valida la nota.
        
        Args:
            valor: Nueva nota (debe estar entre 0 y 20)
            
        Raises:
            ValueError: Si la nota no es válida
        """
        if valor is None:
            raise ValueError("La nota no puede ser None")
        if valor < 0 or valor > 20:
            raise ValueError("La nota debe estar en 0..20")
        self.__nota = valor

    def ejecutar_evaluacion(self):
        """Ejecuta la evaluación (placeholder)."""
        print("Ejecutando evaluación...")

    def __str__(self):
        return f"Evaluacion(nota={self.__nota}, tiempo={self.tiempo_evaluacion}min)"
