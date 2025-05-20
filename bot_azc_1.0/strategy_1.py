
""" MODULO DE ESTRATEGIA 1: BB + VWAP + RSI """
# ===== IMPORTS =====
import pprint
import os
import time
import datetime as dt
import numpy as np
import pandas as pd
import ta
import ta.trend
import BingX
import Modos_de_gestion_operativa as mgo
from backtesting_custom import Backtest, Strategy
from backtesting_custom.lib import crossover


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

#bingx = BingX.BingX(entradas)

# Función para obtener y guardar velas en CSV desde un exchange
def get_velas_df(exchange: str, symbol: str, temporalidad: list, cantidad: list):

    def conv_pdataframe(velas: list, temp: str):
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

        base_dir = "data_velas"
        ruta = os.path.join(base_dir, exchange, symbol, temp)
        os.makedirs(ruta, exist_ok=True)

        fecha = dt.datetime.now().strftime('%Y-%m-%d')
        nombre_archivo = f"{exchange}_{symbol}_{temp}_{fecha}_velas.csv"
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

    # Validación de entradas
    if len(temporalidad) != len(cantidad):
        print("Error: las listas 'temporalidad' y 'cantidad' deben tener la misma longitud.")
        return

    # Lógica por exchange
    if exchange == "BingX":
        bingx = BingX.BingX(entradas)  # 'entradas' debe estar definida
        symbol = str(symbol).upper() + "-USDT"
        for temp, cant in zip(temporalidad, cantidad):
            velas = bingx.get_last_candles(symbol, temp, cant)
            velas.pop(0)  # Remueve encabezado
            if not velas or not isinstance(velas, list):
                print(f"No se recibieron velas para {temp}")
                continue
            conv_pdataframe(velas, temp)
            time.sleep(1)

    elif exchange == "Binance":
        pass
    elif exchange == "OKX":
        pass
    elif exchange == "Bybit":
        pass
    elif exchange == "Phemex":
        pass


def exportar_trades(bt, stats, nombre_base="trades_completo", carpeta="resultados"):
    try:
        # Crear carpeta si no existe
        os.makedirs(carpeta, exist_ok=True)

        # Fecha y hora para identificar cada ejecución
        timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        # Construir nombre final del archivo con timestamp
        nombre_archivo = f"{nombre_base}_{timestamp}.csv"
        ruta_final = os.path.join(carpeta, nombre_archivo)

        # Obtener los DataFrames
        df_trades = stats['_trades'].copy()
        df_debug = pd.DataFrame(stats._strategy.logs_trades)

        # Fusionar si hay índices comunes
        if 'EntryBar' in df_trades.columns and 'bar_index' in df_debug.columns:
            df_merged = pd.merge(df_trades, df_debug, left_on='EntryBar', right_on='bar_index', how='left')
        else:
            df_merged = pd.concat([df_trades, df_debug], axis=1)

        # Exportar
        df_merged.to_csv(ruta_final, index=False)
        print(f"[OK] Exportado como: {ruta_final} ({len(df_merged)} trades)")
    except Exception as e:
        print(f"\n[ERROR] No se pudo exportar: {e}\n")


""" Datos para la Obtención de velas """
exchange = "BingX"
symbol = "near"
temporalidad = ["1m", "3m", "5m"]
cantidad = [1440, 680, 580]

#get_velas_df(exchange, symbol, temporalidad, cantidad)


""" CLASES DE ESTRATEGIA PARA BACKTESTING """

class Long_SMA_MACD_BB(Strategy):
    # Indicadores
    sma = None
    macd = None
    bb_hband = None
    bb_middle = None
    bb_lband = None
    bb_hband_mayor = None
    bb_middle_mayor = None
    bb_lband_mayor = None

    # Flags de lógica
    macd_crossed = False
    ventana_restante = 0

    # Logs para debug de trades
    logs_trades = []

    # Parámetros de los indicadores
    sma_period = 100        # 0 - 200 Periodo de la media movil simple
    macd_fast = 10          # 0 - 12 Periodo rápido del MACD
    macd_slow = 20          # 0 - 26 Periodo lento del MACD
    macd_signal = 10        # 0 - 10 Periodo de la señal del MACD
    bb_period = 20          # 0 - 100 Periodo de las bandas de Bollinger
    bb_std_dev = 1          # 0 - 2 Desviación estándar para las bandas de Bollinger
    # Bandas de Bollinger Mayor
    bb_period_mayor = 20   # 0 - 100 Periodo de las bandas de Bollinger mayor
    bb_std_dev_mayor = 2    # 0 - 2 Desviación estándar para las bandas de Bollinger Mayor

    # Parámetros de gestión de riesgo
    pip_moneda = 1
    pip_precio = 0.0001
    dist_min = 0.5         # % 0 - 1 Distancia mínima entre el precio de entrada y el stop loss
    sep_min = 25           # % de 0 - 100 ampliación de dist entre min_price y precio de entrada
    ratio = 2              # Take profit = riesgo * 2 ej: beneficio/riesgo 2:1
    riesgo_pct = 0.001      # % del capital por operación, 0.001 EQUIVALE A 1 USD PARA UN CAPITAL DE 1000 USD

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

        # Bandas de Bollinger Mayor
        self.bb_hband_mayor = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period_mayor, window_dev = self.bb_std_dev_mayor).bollinger_hband().values,
            self.data.Close)

        self.bb_middle_mayor = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period_mayor, window_dev = self.bb_std_dev_mayor).bollinger_mavg().values,
            self.data.Close)

        self.bb_lband_mayor = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period_mayor, window_dev = self.bb_std_dev_mayor).bollinger_lband().values,
            self.data.Close)

        # contador de señal MACD activa
        self.macd_crossed = 0

    def next(self):
        # Esperar hasta la vela correspondiente al inicio de la SMA
        if self.i < self.sma_period:
            return

        # Valida que no existan posiciones abiertas
        if self.position:
            return  # No abrir nueva si ya hay una activa

        # Valida que el precio actual NO esté dentro de las bandas de Bollinger mayor
        if self.bb_lband_mayor[-1] < self.sma[-1] < self.bb_hband_mayor[-1]:
            return

        """ Paso 1: cruce MACD, Activar señal MACD si corresponde """

        if not self.macd_crossed:

            # Si el MACD cruza la señal y el precio está por encima de la media móvil:
            if self.data.Close[-1] > self.sma[-1] and crossover(self.macd, self.macd_signal):

            # Si el MACD cruza y se mantiene por encima de la señal y el precio está por debajo de la media móvil:
            #if self.data.Close[-1] > self.sma[-1] and self.macd[-1] > self.macd_signal[-1]:

                self.macd_crossed = True
                self.ventana_restante = self.bb_period
                return

        """ Confirmar toque de la banda """
        # variables para el cruce de la banda superior
        min_price = min(self.data.Low[-(self.bb_period):])
        high = self.data.High[-1]
        low = self.data.Low[-1]

        if high >= self.bb_hband[-1]:
            # Buscar entry_price con incremento desde el cierre anterior
            precios_hist = pd.Series(self.data.Close[-(self.bb_period):].tolist())  # 19 previas
            precio = low
            tope = high
            entry_price = None

            """ Bucle de fuerza bruta para conseguir el precio igual o inmediatamente superior al de la banda de bollinger """
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

            """ Validar estructura (distancia al mínimo) """
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
    # Indicadores
    sma = None
    macd = None
    bb_hband = None
    bb_middle = None
    bb_lband = None
    bb_hband_mayor = None
    bb_middle_mayor = None
    bb_lband_mayor = None
    macd_crossed = None

    # Parámetros de los indicadores
    sma_period = 100        # 0 - 200 Periodo de la media movil simple
    macd_fast = 10          # 0 - 12 Periodo rápido del MACD
    macd_slow = 20          # 0 - 26 Periodo lento del MACD
    macd_signal = 10        # 0 - 10 Periodo de la señal del MACD
    bb_period = 20          # 0 - 100 Periodo de las bandas de Bollinger
    bb_std_dev = 1          # 0 - 2 Desviación estándar para las bandas de Bollinger
    # Bandas de Bollinger Mayor
    bb_period_mayor = 20   # 0 - 100 Periodo de las bandas de Bollinger mayor
    bb_std_dev_mayor = 2    # 0 - 2 Desviación estándar para las bandas de Bollinger Mayor

    # Parámetros de gestión de riesgo
    pip_moneda = 1
    pip_precio = 0.0001
    dist_min = 0.5         # % 0 - 1 Distancia mínima entre el precio de entrada y el stop loss
    sep_min = 25           # % de 0 - 100 ampliación de dist entre min_price y precio de entrada
    ratio = 2              # Take profit = riesgo * 2 ej: beneficio/riesgo 2:1
    macd_valid_window = 20 # duración del cruce MACD como señal válida
    riesgo_pct = 0.001      # % del capital por operación, 0.001 EQUIVALE A 1 USD PARA UN CAPITAL DE 1000 USD

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

        # Bandas de Bollinger Mayor
        self.bb_hband_mayor = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period_mayor, window_dev = self.bb_std_dev_mayor).bollinger_hband().values,
            self.data.Close)

        self.bb_middle_mayor = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period_mayor, window_dev = self.bb_std_dev_mayor).bollinger_mavg().values,
            self.data.Close)

        self.bb_lband_mayor = self.I(
            lambda x: ta.volatility.BollingerBands(pd.Series(x), window = self.bb_period_mayor, window_dev = self.bb_std_dev_mayor).bollinger_lband().values,
            self.data.Close)

        # contador de señal MACD activa
        self.macd_crossed = 0

    def next(self):
        # Valida que existan mas de 20 velas para evitar errores
        if len(self.data) < 20: #self.sma_period:
            return

        # Valida que no existan posiciones abiertas
        if self.position:
            return  # No abrir nueva si ya hay una activa

        # Valida que el precio actual NO esté dentro de las bandas de Bollinger mayor
        if self.bb_lband_mayor[-1] < self.sma[-1] < self.bb_hband_mayor[-1]:
            return

        """ Activar señal MACD si corresponde """
        # Si el MACD cruza la señal y el precio está por encima de la media móvil:
        if self.data.Close[-1] < self.sma[-1] and crossover(self.macd_signal, self.macd):

        # Si el MACD cruza y se mantiene por debajo de la señal y el precio está por encima de la media móvil:
        #if self.data.Close[-1] < self.sma[-1] and self.macd[-1] < self.macd_signal[-1]:

            self.macd_crossed = self.macd_valid_window

        if self.macd_crossed > 0:
            self.macd_crossed -= 1
        else:
            return

        """ Confirmar toque de la banda """
        # variables para el cruce de la banda inferior
        max_price = max(self.data.High[-(self.bb_period):])
        high = self.data.High[-1]
        low = self.data.Low[-1]

        if low <= self.bb_lband[-1]:
            # Buscar entry_price con incremento desde el cierre anterior
            precios_hist = pd.Series(self.data.Close[-(self.bb_period):].tolist())  # 19 previas
            precio = high
            tope = low
            entry_price = None

            """ Bucle de fuerza bruta para conseguir el precio igual o inmediatamente superior al de la banda de bollinger """
            while precio >= tope:

                # Calcular banda de Bollinger superior para el precio iterado
                serie = pd.concat([precios_hist, pd.Series([precio])], ignore_index=True)
                bb = ta.volatility.BollingerBands(
                    serie,
                    window = self.bb_period,
                    window_dev = self.bb_std_dev
                    )
                bb_val = bb.bollinger_lband().iloc[-1]

                # Comprobación del precio iterado para cerra el bucle
                if bb_val <= precio and precio < max_price:
                    entry_price = mgo.redondeo(precio, self.pip_precio)
                    break

                # Si no se cumple, incrementar el precio iterado
                precio -= self.pip_precio

            if entry_price is None:
                return  # No se encontró cruce válido

            """ Validar estructura (distancia al mínimo) """
            if (abs(entry_price - max_price) / entry_price * 100) < (self.dist_min / 100):
                return

            # Calcular SL, TP, tamaño
            stop_price = entry_price + (abs(max_price - entry_price) * (1 + self.sep_min / 100))
            risk = abs(entry_price - stop_price)
            take_profit = abs(entry_price - risk * self.ratio)
            riesgo_usd = self.equity * self.riesgo_pct
            cant_mon = riesgo_usd / risk

            cant_mon = mgo.redondeo(cant_mon, self.pip_moneda)
            stop_price = mgo.redondeo(stop_price, self.pip_precio)
            take_profit = mgo.redondeo(take_profit, self.pip_precio)

            if cant_mon > 0: # aquí se debe comprobar si el tamaño es mayor al minimo permitido por el exchange
                self.sell(size = cant_mon, sl = stop_price, tp = take_profit, market = entry_price)


""" ===== Ejecución del BACKTESTING ===== """

data = pd.read_csv("data_velas/BingX/NEAR-USDT/1m/BingX_NEAR-USDT_1m_2025-05-18_velas.csv",
                    parse_dates=['Time'], index_col='Time')

#"""
# Backtest del LONG
bt_long = Backtest(data, Long_SMA_MACD_BB, cash = 1000)
print("\n===== Gestion LONG =====")
stats_long = bt_long.run()
#print(stats_long)
data_long_trades = stats_long['_trades']
print(data_long_trades)
#bt_long.plot()(filename='grafico_long.html')
exportar_trades(bt_long, stats_long, nombre_base="trades_long", carpeta="resultados")
"""
# Backtest del SHORT
bt_short = Backtest(data, Short_SMA_MAC_DBB, cash = 1000)
print("\n===== Gestion SHORT =====")
stats_short = bt_short.run()
print(stats_short)
data_short_trades = stats_short['_trades']
print(data_short_trades)
#bt_short.plot()(filename='grafico_short.html')
#"""
