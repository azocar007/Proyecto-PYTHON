# VARIABLES, no se requiere realizar la declaración de las variables, pero deben ser definidas desde el principio con algun valor
# Al emplear punto y coma ";" al finalizar la declaración de una variable es lo mismo que definir las variables en lineas distantas. si no se emplea el ";" podemos tener error al declarar las variables en la misma linea.
"""
#numero1 = 10; numero2 = 20
#print(numero1)
#print(numero2)

numero3 = 40
numero4 = 50
#print(numero3)
#print(numero4)

# Las variables
# No deben empezar por un valor numerico, no pueden tener caracteres especiales en ninguna parte y solo se puede emplear el guion bajo "_", no se pueden emplear palabras reservadas del sistema y tampoco se pueden emplear espacios, en este caso se emplean los guines bajos.
# Python hace diferencia entre mayusculas y minusculas, por lo cual una misma palabra escrita con mayusculas y minusculas en cualquier parte del texto es interpretada como una variable distinta. 
# numericas int() negativas o positivas, con decimales float() negativas o positivas el decimal debe ser identificado con punto "."
# texto o cadena de texto str(), se identifican con comillas dobles o simples, pero no deben mezclarse.
# Buleanos falso y verdadero True y False con la letra inicail en mayusculas.
# Tambien existen palabras reservadas que identifican los operadores de funciones.
# Las constantes no existen en Python, pero como convencion general se identifican con todas las letras en mayusculas.
numero5 = 87
# Funciones con listas:
#mi_tupla = (numero1, numero2, numero3, numero4)
#print(mi_tupla.index(numero4))
#print(mi_tupla.count(numero4))

# funciones de STRINGS
#    nombre = input("introduzca el nombre\n").capitalize() 
# Vuelve la primera letra de un string en mayusculas y vuelve las demas en minusculas
# .upper convierte todas la letras en mayusculas
# .lower convierte todas las letras en minusculas
"""
numero1 = float(input("Ingrese 1er numero\n"))
numero2 = float(input("Ingrese 2do numero\n"))
if numero1 > numero2:
    print("1er numero es mayor que 2do numero")
else:
    print("2do numero es mayor  que 1er numero")