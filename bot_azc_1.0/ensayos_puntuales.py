""" MODULO DE ESTRATEGIA 1: BB + VWAP + RSI """
# ===== IMPORTS =====
import pprint
import os
import time
import datetime as dt
import numpy as np
import pandas as pd
import Modos_de_gestion_operativa as mgo
import tecnical_analisys as tap
from strategy_1 import exportar_trades
from backtesting_custom import Backtest, Strategy
from backtesting_custom.lib import crossover


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
    ventana = 0

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
        self.logs_trades = []

    def next(self):
        if len(self.data.Close) < self.sma_period:
            return

        if self.position:
            return

        # Calcular indicadores
        close_series = pd.Series(self.data.Close[:])
        high_series = pd.Series(self.data.High[:])
        low_series = pd.Series(self.data.Low[:])

        sma_series = tap.sma(close_series, self.sma_period)
        macd_line, macd_signal_line, _ = tap.macd(close_series, self.macd_fast, self.macd_slow, self.macd_signal)
        bb_upper, bb_middle, bb_lower = tap.bollinger_bands(close_series, self.bb_period, self.bb_std_dev)

        # Tomar el último valor válido
        sma_val = sma_series.iloc[-1]
        macd_val = macd_line.iloc[-1]
        macd_sig_val = macd_signal_line.iloc[-1]
        bb_up_val = bb_upper.iloc[-1]

        """ Paso 1: cruce MACD, Activar señal MACD si corresponde """
        if not self.macd_crossed:
            # Si el MACD cruza la señal y el precio está por encima de la media móvil:
            #if self.data.Close[-1] > sma_val and crossover(macd_line, macd_signal_line):

            # Si el MACD cruza y se mantiene por encima de la señal y el precio está por debajo de la media móvil:
            if self.data.Close[-1] > sma_val and macd_val > macd_sig_val:
                self.macd_crossed = True
                self.ventana = 0
            else:
                return

        """ Paso 2: Confirmar toque de la banda """
        if self.macd_crossed:
            if self.data.High[-1] > bb_up_val and self.ventana > 0:
                min_price = min(self.data.Low[-self.bb_period:])
                tope = self.data.High[-1]
                precio = mgo.redondeo(self.data.Low[-1], self.pip_precio)  # se inicia desde el valor más bajo de la vela actual
                entry_price = None # self.data.Close[-1]
                precios_hist = close_series.iloc[-(self.bb_period - 1):].tolist()

                """ Bucle de fuerza bruta para conseguir el precio igual o inmediatamente superior al de la banda de bollinger """
                while precio <= tope:

                    # Calcular banda de Bollinger superior para el precio iterado
                    serie = pd.Series(precios_hist + [precio])
                    upper, _, _ = tap.bollinger_bands(serie, self.bb_period, self.bb_std_dev)

                    # Comprobación del precio iterado para cerra el bucle
                    if upper.iloc[-1] >= precio:
                        entry_price = mgo.redondeo(precio, self.pip_precio)
                        break

                    # Si no se cumple, incrementar el precio iterado
                    precio += self.pip_precio

                if entry_price is None:
                    self.macd_crossed = False
                    self.ventana = 0
                    return

                """ Validar estructura (distancia al mínimo) """
                dist_pct = abs(entry_price - min_price) / entry_price * 100
                if dist_pct < self.dist_min:
                    self.macd_crossed = False
                    self.ventana = 0
                    return

                # Calcular SL, TP, tamaño
                stop = entry_price - abs(entry_price - min_price) * (1 + self.sep_min / 100)
                risk = abs(entry_price - stop)
                tp = entry_price + risk * self.ratio
                riesgo_usd = self.equity * self.riesgo_pct
                size = riesgo_usd / risk

                size = mgo.redondeo(size, self.pip_moneda)
                stop = mgo.redondeo(stop, self.pip_precio)
                tp = mgo.redondeo(tp, self.pip_precio)

                if size > 0:
                    self.logs_trades.append({
                        'bar_index': len(self.data.Close),
                        'entry_price': entry_price,
                        'macd': macd_val,
                        'macd_signal': macd_sig_val,
                        'sma': sma_val,
                        'bb_upper': bb_up_val,
                        'stop': stop,
                        'tp': tp,
                        'size': size,
                        'time': self.data.index[-1],
                        'ventana': self.ventana,
                        'macd_crossed': self.macd_crossed
                    })
                    self.buy(size=size, sl=stop, tp=tp, market=entry_price)

            else:
                # Si no se cumple el toque de la banda, se reduce la ventana
                self.ventana += 1
                if self.ventana >= self.bb_period:
                        self.macd_crossed = False
                        self.ventana = 0

        #else:
        #    self.macd_crossed = False
        #    self.ventana = 0

        def on_trade_exit(self, trade):
            self.macd_crossed = False
            self.ventana = 0


    """ ===== Ejecución del BACKTESTING ===== """

if __name__ == "__main__":

    data = pd.read_csv("data_velas/BingX/NEAR-USDT/1m/BingX_NEAR-USDT_1m_2025-05-18_velas.csv",
                        parse_dates=['Time'], index_col='Time')

    #"""
    # Backtest del LONG
    bt_long = Backtest(data, Long_SMA_MACD_BB, cash = 1000)
    print("\n\n ============== Gestion LONG ============== ")
    stats_long = bt_long.run()
    print(stats_long)
    data_long_trades = stats_long['_trades']
    print(data_long_trades)
    #exportar_trades(bt_long, stats_long, nombre_base="NEAR_LONG", carpeta="resultados")
    #bt_long.plot()(filename='grafico_long.html')
    #"""
