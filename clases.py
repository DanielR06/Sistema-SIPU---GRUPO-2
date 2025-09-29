class Usuario:
    def __init__(self, nombre, email):
        print(f"Usuario creado con exito: {nombre}, {email}")
        self.nombre = nombre
        self.email = email
        self.rol = None
        

    def iniciarSesion(self):
        print("Iniciando sesion")

    def cerrarSesion(self):
        print("Cerrando sesion")

    def actualizarDatos(self, emailNuevo):
        self.email = emailNuevo
        print("email actualizado correctamente")

class Evaluacion:
    minutosDeEvaluacion=90
    def __init__(self, nota, tipoDeEvaluacion, laboratorio):
        self.nota=nota
        self.tipoDeEvaluacion=tipoDeEvaluacion
        self.laboratorio=laboratorio
    
    def ejecutarEvaluacion(self):
        print("Ejecutando evaluacion")
    
    def cancelarEvaluacion(self):
        print("Evaluacion cancelada")

class Universidad:
    pass

class Carrera:
    pass    

class Nota:
    pass



