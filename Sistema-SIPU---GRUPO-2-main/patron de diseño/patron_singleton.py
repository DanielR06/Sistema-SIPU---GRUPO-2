from typing import List

class Universidad:
    _instancia = None  # Guardará la única instancia

    def __new__(cls, *args, **kwargs):
        if cls._instancia is None:
            cls._instancia = super(Universidad, cls).__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self, nombre_university: str, sedes: List[str]):
        if getattr(self, "_inicializado", False):
            return

        self.nombre_universidad = nombre_university
        self.sedes = sedes
        self._inicializado = True

    def mostrar_datos(self):
        return f"Universidad: {self.nombre_universidad} | Sedes: {', '.join(self.sedes)}"


if __name__ == "__main__":
    uleam = Universidad(
        nombre_university="Universidad Laica Eloy Alfaro de Manabí",
        sedes=["Manta", "Chone"]
    )

    utm = Universidad(
        nombre_university="Universidad Técnica de Manabí",
        sedes=["Portoviejo"]
    )

    print("--- Verificación de Singleton ---")
    print(f"Datos de 'uleam': {uleam.mostrar_datos()}")
    print(f"Datos de 'utm': {utm.mostrar_datos()}")

    print(f"\n¿Ambas variables apuntan al mismo objeto?: {uleam is utm}")
    if uleam is utm:
        print("Resultado: El patrón Singleton evitó la creación de una segunda universidad.")
