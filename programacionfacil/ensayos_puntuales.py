# ensayos preliminares

#import Entrada_de_datos
#import otro

"""listaa = Entrada_de_datos.entrada_de_datos()
#listaa = ["hola", 2, 2.5, 36]
otro.printeando(listaa)
otro.printeando(len(listaa))
otro.printeando(listaa[1])
#otro.printeando(listaa.index(2.5))"""

#datoscorrectos = input("\n¿Esta conforme con los datos ingresados?\n(si/no): ").lower()
def validar_numero_str(mensaje="Ingresa el valor: "):
    while True:
        user_input = input(mensaje)
        try:
            float(user_input) # Intentamos convertir el input a float
            return user_input
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número.")


datoscorrectos = validar_numero_str()
if "." in datoscorrectos:
    datoscorrectos = abs(datoscorrectos.find(".") + 1 - len(datoscorrectos))
else:
    datoscorrectos = 0
print(datoscorrectos)