# otro

# print("hola mundo")

# Corchetes " [] ": Alt Gr + corchete abrir - ASCII Alt + 91 (abrir)        Alt + 93 (cerrar)
# Llaves " {} " : ASCII Alt + 123 (abrir)       Alt + 125 (cerrar)


# import math # se usa para emplear operaciones matematicas complejas

# Do while

import math # se usa para emplear operaciones matematicas complejas
numero = int(input("Ingrese un numero: "))
while numero<11: # isinstance(numero,(int, float)) and
    print("El valor solicitado es menor que 11")
    numero = numero + 1
    print("Ahora es: ", numero)
print(f"\nSu raiz cuadrada es: {(math.sqrt(numero)): .2f}")