# ensayos preliminares

#import Entrada_de_datos
#import otro

"""listaa = Entrada_de_datos.entrada_de_datos()
#listaa = ["hola", 2, 2.5, 36]
otro.printeando(listaa)
otro.printeando(len(listaa))
otro.printeando(listaa[1])
#otro.printeando(listaa.index(2.5))

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
"""

opciones_de_exchanges = {
    "1": "BINANCE",
    "2": "BYBIT",
    "3": "PHEMEX",
    "4": "BING X",
    "5": "OKX",
    "6": "BITGET",
}


def seleccionar_opcionn(opciones: dict, mensaje: str):
    """Función genérica para validar opciones de menú"""
    opciones_formateadas = "\n".join([f"{clave}: {valor}" for clave, valor in opciones.items()])

    while True:
        seleccion = input(f"\n📌 Opciones disponibles:\n{opciones_formateadas}\n{mensaje} ").strip()
        if seleccion in opciones:
            return opciones[seleccion]
        print("❌ Opción inválida. Intente de nuevo.")

exchange_seleccionado = seleccionar_opcionn(opciones_de_exchanges, "Seleccione el exchange (1-6):")
print(exchange_seleccionado)


""" ESTA SECUENCIA DE CODIGO  DEBE EMPLEAR PARA CALCULAR LA CANTIDAD DE DECIMALES EN LAS MONEDAS Y LOS PRECIOS
        if modo_seleccion_volumen == "USDT":
            if (gestion_seleccionada == "UNIDIRECCIONAL SHORT" or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT"):
                cantidad_monedas_short = round(float(monto_de_sl) / entrada_short, cant_decimales_sl)
                cantidad_monedas = cantidad_monedas_short
                cantidad_usdt_short = round(cantidad_monedas_short * entrada_short, 2)
                cantidad_usdt_long = "N/A"
                cantidad_monedas_long = "N/A"
            elif (gestion_seleccionada == "UNIDIRECCIONAL LONG" or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG"):
                cantidad_monedas_long = round(float(monto_de_sl) / entrada_long, cant_decimales_sl)
                cantidad_monedas = cantidad_monedas_long
                cantidad_usdt_long = round(cantidad_monedas_long * entrada_long, 2)
                cantidad_usdt_short = "N/A"
                cantidad_monedas_short = "N/A"
            else:
                cantidad_monedas_long = round(float(cantidad_monedas1) / entrada_long, cantidad_decimales_monedas)
                cantidad_monedas = cantidad_monedas_short = cantidad_monedas_long
                cantidad_usdt_long = round(cantidad_monedas_long * entrada_long, 2)
                cantidad_usdt_short = round(cantidad_monedas_short * entrada_short, 2)
        else:  # modo_seleccion_volumen == "MONEDAS":
            cantidad_monedas = cantidad_monedas_long = cantidad_monedas_short = cantidad_monedas1
            if gestion_seleccionada == "UNIDIRECCIONAL SHORT":
                cantidad_usdt_short = round(float(cantidad_monedas) * entrada_short, 2)
                cantidad_monedas_long = "N/A"
                cantidad_usdt_long = "N/A"
            elif gestion_seleccionada == "UNIDIRECCIONAL LONG":
                cantidad_usdt_long = round(float(cantidad_monedas) * entrada_long, 2)
                cantidad_monedas_short = "N/A"
                cantidad_usdt_short = "N/A"
            else:
                cantidad_usdt_long = round(float(cantidad_monedas) * entrada_long, 2)
                cantidad_usdt_short = round(float(cantidad_monedas) * entrada_short, 2)
"""
