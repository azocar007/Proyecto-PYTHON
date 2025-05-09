
""" MODULO DE ESTRATEGIA 1: BB + VWAP + RSI """
# ===== IMPORTS =====
import pprint
import os
import datetime as dt
import numpy as np
import pandas as pd
import ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import ta.trend

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

    if not velas or not isinstance(velas, list):
        print("No se recibieron velas.")
        return

    df = pd.DataFrame(velas)
    df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'time': 'Time'
    }, inplace=True)

    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df.set_index('Time', inplace=True)
    df.sort_index(inplace=True)

    #print(f"Nuevas velas descargadas: {len(df)}")
    #print(df)

    base_dir = "data_velas"
    ruta = os.path.join(base_dir, exchange, symbol)
    os.makedirs(ruta, exist_ok=True)

    fecha = dt.datetime.now().strftime('%Y-%m-%d')
    nombre_archivo = f"{exchange}_{symbol}_{temporalidad}_{fecha}_velas.csv"
    archivo_completo = os.path.join(ruta, nombre_archivo)

    if os.path.exists(archivo_completo):
        df_existente = pd.read_csv(archivo_completo, parse_dates=['Time'], index_col='Time')
        total_antes = len(df_existente)
        df_total = pd.concat([df_existente, df])
        df_total = df_total[~df_total.index.duplicated(keep='last')]
        df_total.sort_index(inplace=True)
        total_despues = len(df_total)
        nuevas_agregadas = total_despues - total_antes
        df_total.to_csv(archivo_completo)
        print(f"Archivo actualizado: {archivo_completo}")
        print(f"→ Velas nuevas agregadas: {nuevas_agregadas}")
        print(f"→ Total de velas en archivo: {total_despues}")
    else:
        df.to_csv(archivo_completo)
        print(f"Archivo nuevo guardado: {archivo_completo}")
        print(f"→ Velas guardadas: {len(df)}\n")

exchange = "BingX"
symbol = "SUI-USDT"
temporalidad = "1m"
cantidad = 1440

#get_velas_df(exchange, symbol, temporalidad, cantidad)

data = pd.read_csv("data_velas/BingX/SUI-USDT/BingX_SUI-USDT_1m_2025-05-09_velas.csv", parse_dates=['Time'], index_col='Time')
#print("Los datos son:\n", data)

""" CLASES DE ESTRATEGIA PARA BACKTESTING """

class Long_SMA_MACD_BB(Strategy):
    # Indicadores
    sma = None
    macd = None
    bb_hband = None
    bb_middle = None
    bb_lband = None

    # Parámetros de los indicadores
    sma_period = 200
    macd_fast = 10
    macd_slow = 20
    macd_signal = 10
    bb_period = 20
    bb_std_dev = 1

    # Parámetros de gestión de riesgo
    riesgo_pct = 0.01      # 1% del capital por operación
    tp_mult = 2            # Take profit = riesgo * 2

    def init(self):
        """Indicadores de la estrategia"""
        # Media movil
        self.sma = self.I(lambda x: ta.trend.SMAIndicator(pd.Series(x), window = self.sma_period).sma_indicator().values, self.data.Close)

        # MACD
        self.macd, self.macd_signal = self.I(
            lambda x: (
                ta.trend.MACD(pd.Series(x), window_slow = self.macd_slow, window_fast = self.macd_fast, window_sign = self.macd_signal).macd().values,
                ta.trend.MACD(pd.Series(x), window_slow = self.macd_slow, window_fast = self.macd_fast, window_sign = self.macd_signal).macd_signal().values
            ), self.data.Close)

        # Bandas de Bollinger
        self.bb_hband = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period, window_dev = self.bb_std_dev).bollinger_hband().values,
            self.data.Close)

        self.bb_middle = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period, window_dev = self.bb_std_dev).bollinger_mavg().values,
            self.data.Close)

        self.bb_lband = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period, window_dev = self.bb_std_dev).bollinger_lband().values,
            self.data.Close)

    def next(self):

        if len(self.data) < 20:  # Necesario para calcular el mínimo de las 20 últimas velas
            return

        price = self.data.Close[-1]
        b_boll = self.bb_hband[-1]
        low20 = self.data.Low[-20:]
        stop_price = min(low20)
        risk = abs(price - stop_price)

        if risk <= 0:  # Evitar errores por stops inválidos
            return

        take_profit = price + risk * self.tp_mult

        # Condiciones técnicas de entrada long
        if (
            price > self.sma[-1]
            and crossover(self.macd, self.macd_signal) #self.macd[-1] > self.macd_signal[-1]
            and price > b_boll
        ):
            if not self.position:
                # Tamaño basado en riesgo fijo por operación
                capital = self.equity
                riesgo_usd = capital * self.riesgo_pct
                tamaño = abs(riesgo_usd / risk)

                self.buy(size = 40, sl = stop_price, tp = take_profit)
        """
        elif self.position.is_long:
            # Por si se quiere cerrar antes (esto es opcional porque SL/TP ya gestionan salida)
            if (
                price < self.sma[-1] or
                self.macd[-1] < self.macd_signal[-1]
            ):
                self.position.close()
        """


class Short_SMA_MAC_DBB(Strategy):
    sma_period = 200

    def init(self):
        close = self.data.Close

        self.sma = self.I(
            lambda x: SMAIndicator(pd.Series(x), window=self.sma_period).sma_indicator().values,
            close
        )
        self.macd, self.macd_signal = self.I(
            lambda x: (
                MACD(pd.Series(x)).macd().values,
                MACD(pd.Series(x)).macd_signal().values
            ),
            close
        )
        self.bb_middle = self.I(
            lambda x: BollingerBands(pd.Series(x), window=20, window_dev=2).bollinger_mavg().values,
            close
        )

    def next(self):
        price = self.data.Close[-1]
        if (
            price < self.sma[-1] and
            self.macd[-1] < self.macd_signal[-1] and
            price < self.bb_middle[-1]
        ):
            if not self.position:
                self.sell()
        elif self.position.is_short:
            self.position.close()

# Backtest del largo
bt_long = Backtest(data, Long_SMA_MACD_BB)
stats_long = bt_long.run()
print(stats_long)
#bt_long.plot()

"""
# Backtest del corto
bt_short = Backtest(data, Short_SMA_MAC_DBB, cash = 100)
stats_short = bt_short.run()
print(stats_short)
#bt_short.plot()
"""
"""# Backtest de la estrategia MACD + SMA + BB
bt = Backtest(data, MACD_MA_BB, cash = 100)
#bt.run()
stats = bt.run()
print(stats)
#bt.plot()"""

"""
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

class BB_VWAP_RSI(Strategy):
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

"""