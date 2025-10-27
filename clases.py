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
Organizacion de Evaluaciones (General o por area) en linea o virtual
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
#Intanciando un objeto
print("Creando un usuario")
usuario = Usuario("Daniel","daniel24@email.com")
print("Ejecucion del metodo")
usuario.iniciarSesion("ejemplo@mail.com","contraseñasegura")

#Instanciando un segundo objeto
print("Creando un usuario")
usuario2=Usuario("Steph","steph@email.com")
print("Ejecucion del metodo")
usuario.iniciarSesion("ejemplo@mail.com","contraseñasegura")

#Cambio de un atributo
print(f"El usuario 2 es {usuario2.rol}")
print("Cambio de atributo en usuario 2")
usuario2.rol = "administrador"
print(f"El usuario 2 ahora es {usuario2.rol}")

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

print(Aspirante.__bases__) #De que clase se hereda
print(Usuario.__subclasses__) #Que herencias tiene esa clase

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



