from unittest import case


my_string = "mi string"
my_other_string = "mi otro string"
# El comando len() sirve para medir la cantidad de letras de un "string"
print(len(my_string))
print(len(my_other_string))

print(len(my_string)+len(my_other_string))

print(my_string +" y "+ my_other_string)

my_new_line_string = "Este es un string\ncon salto de linea"

print(my_new_line_string)

my_list = ["Nombre: " "Abdías " "Azócar"]

# print(type(my_list))

print(my_list)

print("Hola mundo")


# Intruducir variables con input

"""
print("Por favor, introduzca su nombre.")
Nombre = input()
print("Hola, mucho gusto " + Nombre)
"""
# Calculadora con input()

""""
numero1 = input("ingrese primer numero: ")
numero2 = input("ingrese segundo numero: ")

numero1 = int(numero1)
numero2 = int(numero2)
# Tambien se puede llamar directamente int() desde la definición de la variable

resultado = numero1 + numero2

print("El resutlado es:",resultado)
"""
# Operadores bueleanos
number1 = 50
number2 = 60
print(number1 > number2)
print(number1 < number2)
print(number1 >= number2)
print(number1 <= number2)
print(number1 != number2) # esta cobinacón significa diferente de... 
print(number1 == number2) # esta cobinacón significa igual que...

color1 = "azul"
print(color1 == "azul")

# Operador segun, alternativa a if - else - elif

dia_de_semana = int(input("Ingrese un numero del 1 al 7 para representar el día de semana: "))
match dia_de_semana:
    case 1:
        print("Lunes")
    case 2:
        print("Martes")
    case 3:
        print("Miercoles")
    case 4:
        print("Jueves")
    case 5:
        print("Viernes")
    case 6:
        print("Sabado")
    case 7:
        print("Domingo")
    case _:
        print("la selección no existe ingrese un numero correcto entre 1 y 7")

# Bucle for

numero = 4
for numero in range(numero):
    print(numero+1,"hola")
print("fin")

# bucle while, buscar el cuadrado de un numero.

import math # se usa para emplear operaciones matematicas complejas
numero = int(input("Ingrese un numero: "))
while numero<11:
    print("El valor solicitado es menor que 11")
    numero = numero + 1
    print("Ahora es: ", numero)
print(f"\nSu raiz cuadrada es: {(math.sqrt(numero)): .2f}")

