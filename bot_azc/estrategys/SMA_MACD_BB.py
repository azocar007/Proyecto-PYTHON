import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.volatility import BollingerBands


class SMA_MACD_BB_Long:
    def __init__(
        self,
        df: pd.DataFrame,
        sma_window: int = 100,
        bb1_window: int = 20,
        bb1_dev: float = 2.0,
        bb2_window: int = 20,
        bb2_dev: float = 1,
        macd_fast: int = 10,
        macd_slow: int = 20,
        macd_signal: int = 10,
    ):
        self.df = df.copy().reset_index(drop=True)
        self.sma_window = sma_window
        self.bb1_window = bb1_window
        self.bb1_dev = bb1_dev
        self.bb2_window = bb2_window
        self.bb2_dev = bb2_dev
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

        self._calcular_indicadores()

    def _calcular_indicadores(self):
        close = self.df['close']

        self.df['sma'] = SMAIndicator(close, window=self.sma_window).sma_indicator()

        bb1 = BollingerBands(close, window=self.bb1_window, window_dev=self.bb1_dev)
        self.df['bb1_lower'] = bb1.bollinger_lband()

        bb2 = BollingerBands(close, window=self.bb2_window, window_dev=self.bb2_dev)
        self.df['bb2_upper'] = bb2.bollinger_hband()

        macd = MACD(close, window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        self.df['macd_line'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()

    def evaluar_entrada(self, last_price: float):
        df = self.df
        n = len(df)
        bb1 = self.bb1_window
        bb2 = self.bb2_window

        for i in range(max(bb1, self.bb2_window, self.sma_window), n):

            # Validación de estructura - BB inferior > SMA
            if df['bb1_lower'][i - 1] <= df['sma'][i - 1]:
                continue

            # Validación de cruce MACD
            if not (df['macd_line'][i - 1] < df['macd_signal'][i - 1] and df['macd_line'][i] > df['macd_signal'][i]):
                continue

            # Confirmación en las siguientes bb1 velas usando last_price
            for j in range(i + 1, i + bb1 + 1):
                if j >= n:
                    break

                if last_price > df['bb2_upper'][j]:
                    stop_loss = df['low'][i - bb2:i].min()
                    return {
                        "precio_entrada": last_price,
                        "stop_loss": stop_loss,
                        "estrategia_valida": True
                    }

        return {"estrategia_valida": False}


class SMA_MACD_BB_Short:
    def __init__(
        self,
        df: pd.DataFrame,
        sma_window: int = 20,
        bb1_window: int = 20,
        bb1_dev: float = 2.0,
        bb2_window: int = 20,
        bb2_dev: float = 2.5,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        confirm_candle_window: int = 20
    ):
        self.df = df.copy().reset_index(drop=True)
        self.sma_window = sma_window
        self.bb1_window = bb1_window
        self.bb1_dev = bb1_dev
        self.bb2_window = bb2_window
        self.bb2_dev = bb2_dev
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.confirm_candle_window = confirm_candle_window

        self._calcular_indicadores()

    def _calcular_indicadores(self):
        close = self.df['close']

        # Indicadores
        self.df['sma'] = SMAIndicator(close, window=self.sma_window).sma_indicator()

        bb1 = BollingerBands(close, window=self.bb1_window, window_dev=self.bb1_dev)
        self.df['bb1_upper'] = bb1.bollinger_hband()

        bb2 = BollingerBands(close, window=self.bb2_window, window_dev=self.bb2_dev)
        self.df['bb2_lower'] = bb2.bollinger_lband()

        macd = MACD(close, window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        self.df['macd_line'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()

    def evaluar_entrada(self):
        pass


class SMA_MACD_BB_Long2:
    def __init__(
        self,
        df: pd.DataFrame,
        sma_window: int = 20,
        bb1_window: int = 20,
        bb1_dev: float = 2.0,
        bb2_window: int = 20,
        bb2_dev: float = 2.5,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
    ):
        self.df = df.copy().reset_index(drop=True)
        self.sma_window = sma_window
        self.bb1_window = bb1_window
        self.bb1_dev = bb1_dev
        self.bb2_window = bb2_window
        self.bb2_dev = bb2_dev
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.confirm_candle_window = bb1_window

        self._calcular_indicadores()

    def _calcular_indicadores(self):
        close = self.df['close']

        # Indicadores
        self.df['sma'] = SMAIndicator(close, window=self.sma_window).sma_indicator()

        bb1 = BollingerBands(close, window=self.bb1_window, window_dev=self.bb1_dev)
        self.df['bb1_lower'] = bb1.bollinger_lband()

        bb2 = BollingerBands(close, window=self.bb2_window, window_dev=self.bb2_dev)
        self.df['bb2_upper'] = bb2.bollinger_hband()

        macd = MACD(close, window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        self.df['macd_line'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()

    def evaluar_entrada(self):
        df = self.df
        c_window = self.confirm_candle_window

        for i in range(max(self.bb1_window, self.bb2_window, self.sma_window, 20), len(df) - c_window):
            # Cruce MACD
            if df['macd_line'][i - 1] < df['macd_signal'][i - 1] and df['macd_line'][i] > df['macd_signal'][i]:
                # BB1 inferior > SMA
                if df['bb1_lower'][i] > df['sma'][i]:
                    # Confirmación en las siguientes c_window velas
                    for j in range(i + 1, i + c_window + 1):
                        if df['close'][j] > df['bb2_upper'][j]:
                            # Mínimo de las 20 velas antes del cruce
                            stop_loss = df['low'][i - 20:i].min()
                            entrada = df['close'][j]
                            return {
                                "precio_entrada": entrada,
                                "stop_loss": stop_loss,
                                "estrategia_valida": True
                            }

        return None

