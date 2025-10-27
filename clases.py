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
    rol = "aspirante"

    #deifiniendo atributos de instancia
    def __init__(self, nombre, correo):
        self.nombre = nombre
        self.correo = correo
    
    #Metodo de instancia 
    def iniciarSesion(self, correo, contraseña):
        correoValido = "ejemplo@mail.com"
        contraseñaValida = "contraseñasegura"
        print("Iniciando sesion")
        if correo==correoValido and contraseña==contraseñaValida:
            print("Credenciales correctas")
        else:
            print("Credenciales incorrectas")

#Implementacion de herencia        
class Administrador(Usuario): #<--- Hereda de la clase Usuario
    def __init__(self, nombre, correo, puesto): #<-- Sin super
        self.nombre = nombre
        self.correo = correo
        self.puesto = puesto
class Aspirante(Usuario):
    def __init__(self,nombre, correo, status):
        super().__init__(nombre, correo)#<-- Usando super ya no se apunta a todos los atributos
        self.status = status

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
    def __init__(self, nombreUniversidad):
        self.nombreUniversidad=nombreUniversidad
class Documento:
    pass
class Notificacion:
    pass
class Reporte:
    pass
class Postulacion:
    pass
class OfertaAcademica:
    pass
class Periodo:
    pass
class Laboratorio:
    pass
class Sede:
    pass
class Matriz:
    pass
class Extension:
    pass
class Carrera:
    pass    

class Nota:
    pass


#Modulo de login
administradores=[["admin1","123"],["admin3","456"]]
aspirantes=[["daniel","software1"],["luis","software2"]] #Estas serian conexiones con la base de datos

def login(bd):#Base de datos de las credenciales
    correo=""
    contraseña=""

    print("Ingrese sus credenciales: ")

    correo=input("correo: ")
    contraseña=input("contraseña: ")
    
    for i in range(len(bd)):
        if bd[i][0] == correo and bd[i][1] == contraseña:
            print("Logueado")
"""
Ejecucion del sistema
"""
if __name__ == "__main__":
    opcion=0
    while True:
        print("====Menu===\n1 : Administrador\n2 : Aspirante\n3 : Salir\n")

        opcion = int(input("Ingrese su opcion: "))

        if opcion == 1 :
            print("Ingresando como Administrador\n")
            login(administradores)

            
        elif opcion == 2 :
            print("Ingresando como aspirante\n")
            login(aspirantes)

        else:
            print("Saliendo del sistema\n")
            break

