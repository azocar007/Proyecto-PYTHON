
""" MODULO DE ESTRATEGIA 1: BB + VWAP + RSI """
# ===== IMPORTS =====
import pprint
import os
import datetime as dt
import numpy as np
import pandas as pd
import ta
from backtesting_custom import Backtest, Strategy
from backtesting_custom.lib import crossover
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
    macd_crossed = None

    # Parámetros de los indicadores
    sma_period = 200        # 0 - 200 Periodo de la media movil simple
    macd_fast = 10          # 0 - 12 Periodo rápido del MACD
    macd_slow = 20          # 0 - 26 Periodo lento del MACD
    macd_signal = 10        # 0 - 10 Periodo de la señal del MACD
    bb_period = 20          # 0 - 100 Periodo de las bandas de Bollinger
    bb_std_dev = 1          # 0 - 2 Desviación estándar para las bandas de Bollinger

    # Parámetros de gestión de riesgo
    pip_moneda = 2
    pip_precio = 0.0001
    dist_min = 0         # % 0 - 1 Distancia mínima entre el precio de entrada y el stop loss
    sep_min = 0           # % de 0 - 100 ampliación de dist entre min_price y precio de entrada
    ratio = 2              # Take profit = riesgo * 2 ej: beneficio/riesgo 2:1
    macd_valid_window = 10 # duración del cruce MACD como señal válida
    riesgo_pct = 0.01      # 1% del capital por operación


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

        # contador de señal MACD activa
        self.macd_crossed = 0

    def next(self):

        if len(self.data) < 20:
            return

        if self.position:
            return  # No abrir nueva si ya hay una activa

        min_price = min(self.data.Low[-20:])
        high = self.data.High[-1]
        low = self.data.Low[-1]

        # Activar señal MACD si corresponde
        if self.data.Close[-1] > self.sma[-1] and self.macd[-1] > self.macd_signal[-1]: #crossover(self.macd, self.macd_signal):
            self.macd_crossed = self.macd_valid_window

        if self.macd_crossed > 0:
            self.macd_crossed -= 1
        else:
            return

        # Confirmar toque de la banda
        if high >= self.bb_hband[-1]:
            # Buscar entry_price con incremento desde el cierre anterior
            precios_hist = pd.Series(self.data.Close[-19:].tolist())  # 19 previas
            precio = low
            tope = high
            entry_price = None

            # Bucle de fuerza bruta para conseguir el precio igual o inmediatamente superior al de la banda de bollinger
            while precio <= tope:

                # Calcular banda de Bollinger superior para el precio iterado
                serie = pd.concat([precios_hist, pd.Series([precio])], ignore_index=True)
                bb = ta.volatility.BollingerBands(
                    serie,
                    window = self.bb_period,
                    window_dev = self.bb_std_dev
                    )
                bb_val = bb.bollinger_hband().iloc[-1]

                # Comprobación del precio iterado para cerra el bucle
                if bb_val >= precio:
                    entry_price = mgo.redondeo(precio, self.pip_precio)
                    break

                # Si no se cumple, incrementar el precio iterado
                precio += self.pip_precio

            if entry_price is None:
                return  # No se encontró cruce válido

            # Validar estructura (distancia al mínimo)
            if (abs(entry_price - min_price) / entry_price * 100) < (self.dist_min / 100):
                return

            # Calcular SL, TP, tamaño
            stop_price = entry_price - (abs(min_price - entry_price) * (1 + self.sep_min / 100))
            risk = abs(entry_price - stop_price)
            take_profit = entry_price + risk * self.ratio
            riesgo_usd = self.equity * self.riesgo_pct
            cant_mon = riesgo_usd / risk

            cant_mon = mgo.redondeo(cant_mon, self.pip_moneda)
            stop_price = mgo.redondeo(stop_price, self.pip_precio)
            take_profit = mgo.redondeo(take_profit, self.pip_precio)

            if cant_mon > 0: # aquí se debe comprobar si el tamaño es mayor al minimo permitido por el exchange
                self.buy(size = cant_mon, sl = stop_price, tp = take_profit, market = entry_price)


class Short_SMA_MAC_DBB(Strategy):
    pass


# Backtest del largo
bt_long = Backtest(data, Long_SMA_MACD_BB, cash = 1000)
stats_long = bt_long.run()
print(stats_long)
data_long_trades = stats_long['_trades']
print(data_long_trades)
#bt_long.plot()(filename='grafico_long.html')
