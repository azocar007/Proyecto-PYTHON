# ENSAYO DE FUNCIONES Y MODULOS
from Entrada_de_datos import validar_numero, contar_decimales

def printeando(ag):
    print(ag)

moneda = validar_numero()
cant = contar_decimales(moneda)
print(moneda, cant)