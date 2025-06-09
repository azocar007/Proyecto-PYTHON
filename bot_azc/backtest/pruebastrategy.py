import ta
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover

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

    # Parámetros
    sma_period = 100
    macd_fast = 10
    macd_slow = 20
    macd_signal = 10
    bb_period = 20
    bb_std_dev = 1
    bb_period_mayor = 20
    bb_std_dev_mayor = 2

    pip_moneda = 1
    pip_precio = 0.0001
    dist_min = 0.5
    sep_min = 25
    ratio = 2
    riesgo_pct = 0.001

    def init(self):
        self.sma = self.I(lambda x: ta.trend.SMAIndicator(pd.Series(x), window=self.sma_period).sma_indicator().values, self.data.Close)

        self.macd, self.macd_signal = self.I(
            lambda x: (
                ta.trend.MACD(pd.Series(x), window_fast=self.macd_fast, window_slow=self.macd_slow, window_sign=self.macd_signal).macd().values,
                ta.trend.MACD(pd.Series(x), window_fast=self.macd_fast, window_slow=self.macd_slow, window_sign=self.macd_signal).macd_signal().values
            ), self.data.Close)

        bb = lambda dev: lambda x: ta.volatility.BollingerBands(pd.Series(x), window=self.bb_period, window_dev=dev)
        bb_mayor = lambda dev: lambda x: ta.volatility.BollingerBands(pd.Series(x), window=self.bb_period_mayor, window_dev=dev)

        self.bb_hband = self.I(lambda x: bb(self.bb_std_dev)(x).bollinger_hband().values, self.data.Close)
        self.bb_lband = self.I(lambda x: bb(self.bb_std_dev)(x).bollinger_lband().values, self.data.Close)
        self.bb_hband_mayor = self.I(lambda x: bb_mayor(self.bb_std_dev_mayor)(x).bollinger_hband().values, self.data.Close)
        self.bb_lband_mayor = self.I(lambda x: bb_mayor(self.bb_std_dev_mayor)(x).bollinger_lband().values, self.data.Close)

    def next(self):
        # Esperar hasta la vela correspondiente al inicio de la SMA
        if self.i < self.sma_period:
            return

        if self.position:
            return

        if self.bb_lband_mayor[-1] < self.sma[-1] < self.bb_hband_mayor[-1]:
            return

        # Paso 1: cruce MACD
        if not self.macd_crossed:
            if self.data.Close[-1] > self.sma[-1] and crossover(self.macd, self.macd_signal):
                self.macd_crossed = True
                self.ventana_restante = self.bb_period
                return

        # Paso 2: detectar toque en banda superior
        if self.macd_crossed:
            self.ventana_restante -= 1
            if self.data.High[-1] >= self.bb_hband[-1]:
                min_price = min(self.data.Low[-self.bb_period:])
                precios_hist = pd.Series(self.data.Close[-(self.bb_period - 1):].tolist())
                precio = self.data.Low[-1]
                tope = self.data.High[-1]
                entry_price = None

                while precio <= tope:
                    serie = pd.concat([precios_hist, pd.Series([precio])], ignore_index=True)
                    bb = ta.volatility.BollingerBands(
                        serie,
                        window=self.bb_period, 
                        window_dev=self.bb_std_dev
                        )
                    bb_val = bb.bollinger_hband().iloc[-1]

                    if bb_val >= precio:
                        entry_price = precio
                        break
                    precio += self.pip_precio

                if entry_price is None:
                    self.macd_crossed = False
                    return

                if (abs(entry_price - min_price) / entry_price * 100) < self.dist_min:
                    self.macd_crossed = False
                    return

                stop = entry_price - abs(entry_price - min_price) * (1 + self.sep_min / 100)
                risk = abs(entry_price - stop)
                tp = entry_price + risk * self.ratio
                riesgo_usd = self.equity * self.riesgo_pct
                size = riesgo_usd / risk

                from Modos_de_gestion_operativa import redondeo
                size = redondeo(size, self.pip_moneda)
                stop = redondeo(stop, self.pip_precio)
                tp = redondeo(tp, self.pip_precio)

                if size > 0:
                    self.logs_trades.append({
                        'bar_index': self.i,
                        'entry_price': entry_price,
                        'sma': self.sma[-1],
                        'macd': self.macd[-1],
                        'macd_signal': self.macd_signal[-1],
                        'bb_upper': self.bb_hband[-1],
                        'bb_upper_mayor': self.bb_hband_mayor[-1],
                        'low_ult_20': min_price,
                        'stop': stop,
                        'tp': tp,
                        'size': size
                    })
                    self.buy(size=size, sl=stop, tp=tp, market=entry_price)

                self.macd_crossed = False

            elif self.ventana_restante <= 0:
                self.macd_crossed = False


    def next(self):
        # Esperar hasta la vela correspondiente al inicio de la SMA
        if self.i < self.sma_period:
            return

        if self.position:
            return

        if self.bb_lband_mayor[-1] < self.sma[-1] < self.bb_hband_mayor[-1]:
            return

        # Paso 1: cruce MACD
        if not self.macd_crossed:
            if self.data.Close[-1] > self.sma[-1] and crossover(self.macd, self.macd_signal):
                self.macd_crossed = True
                self.ventana_restante = self.bb_period
                """ En la recomendación anterior """
                self.vela_cruce_index = len(self.data)  # index de la vela del cruce
                return

        # Paso 2: detectar toque en banda superior
        if self.macd_crossed:
            self.ventana_restante -= 1
            if self.data.High[-1] >= self.bb_hband[-1]:
                min_price = min(self.data.Low[-self.bb_period:])
                min_price = mgo.redondeo(min_price, self.pip_precio)
                precios_hist = pd.Series(self.data.Close[-(self.bb_period - 1):].tolist())
                precio = mgo.redondeo(self.data.Low[-1], self.pip_precio)
                tope = mgo.redondeo(self.data.High[-1], self.pip_precio)
                entry_price = None

                while precio <= tope:
                    serie = pd.concat([precios_hist, pd.Series([precio])], ignore_index=True)
                    bb = ta.volatility.BollingerBands(serie, window=self.bb_period, window_dev=self.bb_std_dev)
                    bb_val = bb.bollinger_hband().iloc[-1]
                    bb_val = mgo.redondeo(bb_val, self.pip_precio)
                                    
                    if bb_val >= precio:
                        entry_price = mgo.redondeo(precio, self.pip_precio)
                        break
                    precio += self.pip_precio

                if entry_price is None:
                    self.macd_crossed = False
                    return

                # Validar estructura técnica
                if (abs(entry_price - min_price) / entry_price * 100) < self.dist_min:
                    self.macd_crossed = False
                    return

                # Calcular SL, TP y tamaño
                stop = entry_price - abs(entry_price - min_price) * (1 + self.sep_min / 100)
                risk = abs(entry_price - stop)
                tp = entry_price + risk * self.ratio
                riesgo_usd = self.equity * self.riesgo_pct
                size = riesgo_usd / risk

                size = mgo.redondeo(size, self.pip_moneda)
                stop = mgo.redondeo(stop, self.pip_precio)
                tp = mgo.redondeo(tp, self.pip_precio)

                if size > 0:
                    self.buy(size=size, sl=stop, tp=tp, market=entry_price)

                self.macd_crossed = False # se consumió la señal

            elif self.ventana_restante <= 0:
                self.macd_crossed = False # se venció la ventana sin señal
