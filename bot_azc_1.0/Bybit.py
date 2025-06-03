### Modulo Bybit Tesnet ###
# Este modulo se encarga de realizar las operaciones de trading en la plataforma Bybit Testnet
import pprint
import time
from pybit.unified_trading import HTTP
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR


session = HTTP(
    testnet=True,
    api_key= 'X2ubLN641kBWsqb0mm',
    api_secret='rU5QWC2vUaOfpg9BPbdPZ5EPwcbNenLKr7tc'
)

symbol = ''  # Puedes ajustar el símbolo según tus necesidades
stop_loss = 0  # Valor en USDT
estado = False
capital = 0

# Extraer información de la moneda seleccionada, todos estos valores estan en STRING
inf_moneda = session.get_instruments_info(category="linear", symbol=symbol)
pip_precio = inf_moneda['result']['list'][0]['priceFilter']['tickSize']
min_usdt = inf_moneda['result']['list'][0]['lotSizeFilter']['minNotionalValue']
cant_decimales_precio = inf_moneda['result']['list'][0]['priceScale']
pip_moneda = inf_moneda['result']['list'][0]['lotSizeFilter']['minOrderQty']

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


def establecer_stop_loss(symbol, price):
    price = qty_step(symbol, price)
    print(price)

    # PONER ORDEN STOP LOSS
    order = session.set_trading_stop(
        category="linear",
        symbol=symbol,
        stopLoss=price,
        slTriggerB="LastPrice",
        positionIdx=0,
    )

    return order


# Lógica del bot (ejemplo simple: compra y venta cada 60 segundos)
while True:
    try:
        if estado:
            # Posiciones Abiertas
            posiciones = session.get_positions(category="linear", symbol=symbol)
            if float(posiciones['result']['list'][0]['size']) != 0:
                precio_de_entrada = float(posiciones['result']['list'][0]['avgPrice'])
                USDT = float(posiciones['result']['list'][0]['positionValue'])
                porcentaje = (stop_loss * 100) / USDT
                aumento = precio_de_entrada * (porcentaje / 100)
                if posiciones['result']['list'][0]['side'] == 'Buy':
                    stop_price = precio_de_entrada - aumento
                else:
                    stop_price = precio_de_entrada + aumento
                if stop_price < 0:
                    print('TU STOP LOSS NO ES POSIBLE, SE ENCUENTRA POR DEBAJO DE CERO')
                else:
                    # poner stop loss
                    if USDT != capital:
                        print('MODIFICANDO STOP LOSS')
                        establecer_stop_loss(symbol, stop_price)
                        capital = USDT
            else:
                session.cancel_all_orders(category="linear", symbol=symbol)
                estado = False
                capital = 0

        else:
            tick = input('INGRESE EL TICK QUE DESEA OPERAR: ').upper()
            if tick != '':
                tick = tick + 'USDT'
                symbol = tick
                stop = float(input('INGRESE EL VALOR MAXIMO EN USDT QUE DESEA PERDER: '))
                if stop != '':
                    stop_loss = stop
                    # Posiciones Abiertas
                    posiciones = session.get_positions(category="linear", symbol=symbol)
                    if float(posiciones['result']['list'][0]['size']) != 0:
                        print('POSICION ABIERTA EN ' + symbol)
                        estado = True

                    else:
                        print('NO HAY NINGUNA POSICION ABIERTA EN ' + symbol)
                else:
                    print('EL DATO INGRESADO NO ES VALIDO')
            else:
                print('EL DATO INGRESADO NO ES VALIDO')

    except Exception as e:
        print(f"Error: {e}")
        stop_loss = 0
        estado = False
        capital = 0
        time.sleep(5)
    time.sleep(1)