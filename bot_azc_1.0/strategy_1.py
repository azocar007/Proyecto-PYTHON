
""" MODULO DE ESTRATEGIA 1: BB + VWAP + RSI """
# ===== IMPORTS =====
import pprint
import numpy as np
import pandas as pd
import ta
from backtesting import Backtest, Strategy
from backtesting.test import GOOG
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

velas = bingx.get_last_candles("1m", 5)
velas.pop(0) # Para eliminar el 1er elemento que contiene el simbolo y la temporalidad
print("\ncopilot")
df = mgo.conv_candles(velas)
print(type(df))
print(df)

print("\ngpt")
dfgpt = mgo.conv_gpt(velas)
print(type(dfgpt))
print(dfgpt)



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