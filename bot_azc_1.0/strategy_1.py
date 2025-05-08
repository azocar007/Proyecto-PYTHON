
""" MODULO DE ESTRATEGIA 1: BB + VWAP + RSI """
# ===== IMPORTS =====
import pprint
import numpy as np
import pandas as pd
import ta
import datetime as dt
from datetime import datetime
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

import BingX
import Modos_de_gestion_operativa as mgo

entradas = {
                "symbol": "doge",
                "positionside": "LONG",
                "modo_gestion": "REENTRADAS",
                "monto_sl": 1.0,
                "type": "LIMIT",
                "precio_entrada": 0,
                "gestion_take_profit": "RATIO BENEFICIO/PERDIDA",
                "ratio": 2,
                "gestion_vol": "MARTINGALA",
                "cant_ree": 6,
                "dist_ree": 2,
                "porcentaje_vol_ree": 0,
                "monedas": 0,
                "usdt": 0,
                "segundos": 5,
                "temporalidad": "1m"
                }

bingx = BingX.BingX(entradas)

# Función para obtener y guardar velas en CSV desde un exchange
def get_velas_df(exchange, symbol, temporalidad, cantidad):
    # Selección de exchange.
    if exchange == "BingX":
        velas = bingx.get_last_candles(symbol, temporalidad, cantidad)
        velas.pop(0) # Para eliminar el 1er elemento que contiene el simbolo y la temporalidad

    elif exchange == "Binance":
        pass
    elif exchange == "OKX":
        pass
    elif exchange == "Bybit":
        pass
    elif exchange == "Phemex":
        pass

    # Convertimos a DataFrame
    df = pd.DataFrame(velas)

    # Renombramos columnas a formato estándar si es necesario
    df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'time': 'Time'
    }, inplace=True)

    # Convertimos los tipos a float y datetime
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)

    # Convertimos 'Time' a datetime (milisegundos UNIX)
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df.set_index('Time', inplace=True)

    # (Opcional) ordena por tiempo si viene al revés
    df.sort_index(inplace=True)

    print(f"Longitud del diccionario de velas {len(df)}")
    print(df)

    # variables para nombre de archivo
    fecha = dt.datetime.now().strftime('%Y-%m-%d')  # Formato YYYY-MM-DD
    nombre_archivo = f"{exchange}_{symbol}_{temporalidad}_{fecha}_{cantidad}_velas.csv"

    df.to_csv(nombre_archivo)  # Guardar el DataFrame en un archivo CSV

    return df


""" Codigo de la estrategia CHATGPT """

# Creamos un script base para recibir velas, almacenar en CSV y aplicar estrategia
def procesar_vela_nueva(vela, archivo='datos.csv'):
    # Intentamos cargar el CSV existente
    try:
        df = pd.read_csv(archivo, parse_dates=['Time'], index_col='Time')
    except FileNotFoundError:
        df = pd.DataFrame()

    # Convertimos la nueva vela a DataFrame
    nueva = pd.DataFrame([vela])
    nueva['Time'] = pd.to_datetime(nueva['time'], unit='ms')
    nueva = nueva.drop(columns='time')
    nueva.columns = [col.capitalize() for col in nueva.columns]  # open → Open
    nueva.set_index('Time', inplace=True)
    nueva = nueva.astype(float)

    # Concatenamos y eliminamos duplicados por índice (Time)
    df = pd.concat([df, nueva])
    df = df[~df.index.duplicated(keep='last')]
    df.sort_index(inplace=True)

    # Guardamos actualizado
    df.to_csv(archivo)

    # Aplicamos indicadores y estrategia
    return aplicar_estrategia(df)

def aplicar_estrategia(df):
    from ta.momentum import RSIIndicator
    from ta.volatility import BollingerBands
    from ta.volume import VolumeWeightedAveragePrice

    if len(df) < 20:
        return None  # Esperar suficientes velas para indicadores

    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']

    # Indicadores
    rsi = RSIIndicator(close).rsi()
    bb = BollingerBands(close, window=20, window_dev=2)
    vwap = VolumeWeightedAveragePrice(high, low, close, volume).vwap()

    # Condiciones actuales (última vela)
    precio = close.iloc[-1]
    rsi_val = rsi.iloc[-1]
    vwap_val = vwap.iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    # Lógica de entrada
    if precio <= bb_lower and precio < vwap_val and rsi_val < 40:
        return 'long'

    return None




class BB_VWAP_RSI_TA(Strategy):
    # Parámetros de la estrategia
    bb_period = 20
    bb_std_dev = 2
    vwap_period = 14
    rsi_period = 14

    def init(self):
        # Inicializar indicadores
        self.bb = ta.volatility.BollingerBands(self.data.Close, window=self.bb_period, window_dev=self.bb_std_dev)
        self.vwap = ta.volume.VolumeWeightedAveragePrice(self.data.High, self.data.Low, self.data.Close, self.data.Volume)
        self.rsi = ta.momentum.RSIIndicator(self.data.Close, window=self.rsi_period)

    def next(self):
        # Lógica de trading aquí
        pass


class BB_VWAP_RSI:
    def __init__(self, exchange, symbol, timeframe, bb_period=20, bb_std_dev=2, vwap_period=14, rsi_period=14):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev
        self.vwap_period = vwap_period
        self.rsi_period = rsi_period

    def run(self):
        # Lógica de la estrategia aquí
        # Obtener datos históricos
        df = bingx.get_last_candles(self.timeframe, 500)
        #pprint.pprint(df)
    pass

# ===== EJECUCIÓN PRINCIPAL =====
if __name__ == "__main__":
    strategy = BB_VWAP_RSI(bingx, entradas["symbol"], entradas["temporalidad"])
    strategy.run()