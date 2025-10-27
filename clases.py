""" SISTEMA SIPU (Sistema Incricripcion Postulacuion Universitario)

CLASES PRINCIPALES:
Usuario
Administrador
Aspirante
Evaluacion
Universidad
Documento
Notificacion
Reporte
Postulacion
OfertaAcademica
Periodo 
Laboratorio 
Sede 
Matriz
Extension
Carrera
Nota

Herencias:

Flujo del sistema:
La universidad dispone la OfertaAcademica (Carrera disponibles en cada sede en ese periodo)
El aspirante postula en la universidad (en el periodo actual)
El Sistema consume la api de del registro nacional
Si no tiene registro nacional no es valido
Se selecciona una o mas carreras
Organizacion de Evaluaciones (General o por area) en presencial o virtual
Organacion de jornadas 
Incidencias en examenes(examenes canceladas)
Los estudiantes obtienen sus notas

Inscripccion --> Postulacion --> Evaluacion --> Notas --> Sistema Sac 
"""

class Usuario:
    #atributo de clase
    #deifiniendo atributos de instancia
    def __init__(self, nombre, correo): #Constructor de usuarios
        self.nombre = nombre
        self.correo = correo
    
#Implementacion de herencia        
class Administrador(Usuario): #<--- Hereda de la clase Usuario
    def __init__(self, nombre, correo): #<-- Sin super
        self.nombre = nombre
        self.correo = correo
    def crearUniversidad(nombre, sedes):
        return Universidad(nombre, sedes)

    def crearPerido():
        pass
    def crearCarrera():
        pass
    def crearSedes():
        pass
class Aspirante(Usuario):
    def __init__(self,nombre, correo):
        super().__init__(nombre, correo)#<-- Usando super ya no se apunta a todos los atributos
        self.status = None
    
    def definirEstado(self,estado):
        self.estatus=estado

"""
print(Aspirante.__bases__) #De que clase se hereda
print(Usuario.__subclasses__) #Que herencias tiene esa clase
"""
class Evaluacion:
    def __init__(self,nota, tiempoEvaluacion):
        self.__nota=nota
        self.tiempoEvaluacion= tiempoEvaluacion

    #Encapsulamiento del atributo nota
    @property #Getter
    def nota(self):
        return self.__nota
    
    @nota.setter #Setter
    def nota(self,valor):
        if valor != "":
            print("Modificando valor")
            self.__nota = valor
        else:
            print("El valor esta vacio")

    def ejecutarEvaluacion(self):
        print("Ejecutando evaluacion")
class Universidad:
    def __init__(self, nombreUniversidad, sedes):
        self.nombreUniversidad=nombreUniversidad
        self.sedes=sedes
class Documento:
    pass
class Notificacion:
    pass
class Reporte:
    pass
class Postulacion:
    pass
class OfertaAcademica:
    #1 Universidad
    #1 Periodo
    #Muchas carreras
    #1 Sede
    pass
class Periodo:
    pass
class Laboratorio:
    pass
class Sede:
    #Laboratorios
    pass
class Carrera:
    pass    

class Nota:
    pass


#Modulo de login
db_usuarios = [
    {"correo": "admin1", "contrasena": "123", "rol": "admin"},
    {"correo": "daniel", "contrasena": "software1", "rol": "postulante"},
    {"correo": "admin3", "contrasena": "456", "rol": "admin"},
    {"correo": "luis", "contrasena": "software2", "rol": "postulante"}
]
#Estas serian conexiones con la base de datos]

def login(bd):#Base de datos de las credenciales
    print("===Inicio de sesion===\nIngrese sus credenciales: \n")

    correo=input("correo: ")
    contraseña=input("contraseña: ")
    
    for usuario in bd:
        if usuario["correo"] == correo and usuario["contrasena"] == contraseña:
            if usuario["rol"] == "admin":
                print("Login exitoso. ¡Bienvenido Administrador!")
                return Administrador(correo) # Retorna un objeto Admin
            elif usuario["rol"] == "postulante":
                print("Login exitoso. ¡Bienvenido Postulante!")
                return Aspirante(correo) # Retorna un objeto Aspirante
    print("Error: Credenciales incorrectas.")
    return None
    
"""
Ejecucion del sistema
"""
if __name__ == "__main__":
    opcion=0
    while True:
        print("====Menu===\n1 : Ingresar a sistema \n2 : Salir\n")
        opcion = int(input("Ingrese su opcion: "))
        if opcion == 1 :
            print("Ingresando al sistema\n")
            usuarioActual=login(db_usuarios)
            if isinstance (usuarioActual, Administrador):
                pass
        else: 
            print("Saliendo del sistema\n")
            break
            pass
            

