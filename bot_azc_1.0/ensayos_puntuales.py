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


opciones_de_exchanges = {
    "1": "BINANCE",
    "2": "BYBIT",
    "3": "PHEMEX",
    "4": "BING X",
    "5": "OKX",
    "6": "BITGET",
}


def seleccionar_opcionn(opciones: dict, mensaje: str):
    ""Función genérica para validar opciones de menú""
    opciones_formateadas = "\n".join([f"{clave}: {valor}" for clave, valor in opciones.items()])

    while True:
        seleccion = input(f"\n📌 Opciones disponibles:\n{opciones_formateadas}\n{mensaje} ").strip()
        if seleccion in opciones:
            return opciones[seleccion]
        print("❌ Opción inválida. Intente de nuevo.")

exchange_seleccionado = seleccionar_opcionn(opciones_de_exchanges, "Seleccione el exchange (1-6):")
print(exchange_seleccionado)


ESTA SECUENCIA DE CODIGO  DEBE EMPLEAR PARA CALCULAR LA CANTIDAD DE DECIMALES EN LAS MONEDAS Y LOS PRECIOS
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

import pprint
import time
from pybit.unified_trading import HTTP
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR

symbol = 'DOGEUSDT'  # Puedes ajustar el símbolo según tus necesidades
stop_loss = 0  # Valor en USDT
estado = False
capital = 0

session = HTTP(
    testnet=True,
    api_key= 'X2ubLN641kBWsqb0mm',
    api_secret='rU5QWC2vUaOfpg9BPbdPZ5EPwcbNenLKr7tc'
)
# Extraer información de la moneda seleccionada
inf_moneda = session.get_instruments_info(category="linear", symbol=symbol)
pip_moneda = inf_moneda['result']['list'][0]['priceFilter']['tickSize']
min_usdt = inf_moneda['result']['list'][0]['lotSizeFilter']['minNotionalValue']

cant_decimales_precio = inf_moneda['result']['list'][0]['priceScale']

pprint.pprint(inf_moneda)
print("\nPip de la moneda: ", pip_moneda, type(pip_moneda))
print("\nMínimo de USDT: ", min_usdt, type(min_usdt))
print("\nCantidad de decimales en el precio: ", cant_decimales_precio, type(cant_decimales_precio))

# Codigo para stop loss Gafas

def qty_step(symbol, price):
    step = session.get_instruments_info(category="linear", symbol=symbol)
    ticksize = float(step['result']['list'][0]['priceFilter']['tickSize'])
    scala_precio = int(step['result']['list'][0]['priceScale'])
    precision = Decimal(f"{10**scala_precio}")
    tickdec = Decimal(f"{ticksize}")
    precio_final = (Decimal(f"{price}")*precision)/precision
    precide = precio_final.quantize(Decimal(f"{1/precision}"),rounding=ROUND_FLOOR)
    operaciondec = (precide / tickdec).quantize(Decimal('1'), rounding=ROUND_FLOOR) * tickdec
    result = float(operaciondec)

    return result