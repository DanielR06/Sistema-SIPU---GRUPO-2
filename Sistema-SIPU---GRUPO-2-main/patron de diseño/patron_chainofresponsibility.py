from abc import ABC, abstractmethod
"""
Clase 'Manejador' de la cadena que valida cada requisito del postulante
Cedula de identidad, Título de Bachiller y Puntaje Mínimo.
"""

class Validador(ABC):
    def __init__(self, siguiente=None):
        self.siguiente = siguiente

    @abstractmethod
    def manejar(self, aspirante):
        # Si hay un siguiente, delegamos por defecto
        if self.siguiente:
            return self.siguiente.manejar(aspirante)
        return "Validación completa: El aspirante cumple todos los requisitos."

# Cedula de identidasd
class ValidadorCedula(Validador):
    def manejar(self, aspirante):
        if not aspirante.get("tiene_cedula"):
            return "Error: No se encontró un documento de identidad."
        
        print("Cedula verificada.")
        return super().manejar(aspirante)

# Titulo de Bachiller
class ValidadorTitulo(Validador):
    def manejar(self, aspirante):
        if not aspirante.get("titulo_bachiller"):
            return "Error: El aspirante no registra título de bachiller."
        
        print("Título de bachiller verificado.")
        return super().manejar(aspirante)

# Puntaje minimo
class ValidadorPuntaje(Validador):
    def manejar(self, aspirante):
        # Puntaje minimo de esta carrera es 600
        if aspirante.get("puntaje", 0) < 600:
            return f"Error: Puntaje insuficiente ({aspirante.get('puntaje')}). Se requiere mínimo 600."
        
        print("Puntaje verificado.")
        return super().manejar(aspirante)
    
if __name__ == "__main__":
    # 1. Definimos los datos del aspirante (simulando una base de datos o input)
    # Puedes cambiar estos valores para probar los diferentes errores
    aspirante_ejemplo = {
        "nombre": "Daniel",
        "tiene_cedula": True,
        "titulo_bachiller": True,
        "puntaje": 720
    }

    # 2. Construimos la cadena de responsabilidad
    # El orden sugerido es: Puntaje -> Título -> Cédula
    # Cada objeto recibe al "siguiente" en la fila.
    validador_final = ValidadorCedula()
    validador_medio = ValidadorTitulo(siguiente=validador_final)
    cadena_validacion = ValidadorPuntaje(siguiente=validador_medio)

    # 3. Ejecutamos la validación
    print(f"--- Iniciando validación para: {aspirante_ejemplo['nombre']} ---")
    resultado = cadena_validacion.manejar(aspirante_ejemplo)
    
    print("-" * 50)
    print(f"RESULTADO FINAL: {resultado}")