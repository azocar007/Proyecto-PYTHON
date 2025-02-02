# Operadores aritmeticos, son los operadores normales de suma, resta, multiplicación y división ( + - * /)
# el operador de división siempre da como resultado un valor de tipo float() con un decimal por defecto.

numero1 = 4; numero2 = 6
print(numero1)
print(numero2)
print(numero1 + numero2)

numero3 = 40
numero4 = 50
print(numero3)
print(numero4) 
resultado = (numero3 / numero4)
print(resultado)

# Operadores modulo, división entera y potencia

cociente = numero1 / numero2
resto = numero1 % numero2
print(f"Cociente (resultado de la división): {cociente}, Resto: {resto}")

potencia1 = 2 # la potencia de un numero se escribe repitiendo el simblo asterisco dos veces seguidas sin espacios.
resultado_potencia = numero1 ** potencia1

print(resultado_potencia)

# La prioridad en las operaciones aritmeticas se hace de la siguiente manera:
# 1ro exponentes y raices.
# 2do multiplicación y división.
# 3ro sumas y restas.

ejemplo = numero1 + numero2 ** 3 / numero3 
print(ejemplo)

# Numeros largos, para una buena interpretación del usuario se puenen emplear guin bajo "_" en ves de punto o comas ya que stos ultimos simbolos estan dedicados para otras cosas.

numero_largo = 485_269_745_523.4569
print(numero_largo)

# Funciones con listas:

num1 = float(input("Primer numero:\n"))
num2 = float(input("Segundo numero:\n"))
resultado2 = num1 + num2
print(f"El resultado es: {resultado2} en la suma de los valores ingresados")

list_de_numeros = [num1, num2, resultado2] 

num3 = float(input("Ingrese numero:\n"))
list_de_numeros.append(num3)

num4 = float(55)
list_de_numeros.insert(0,num4)

print(list_de_numeros)