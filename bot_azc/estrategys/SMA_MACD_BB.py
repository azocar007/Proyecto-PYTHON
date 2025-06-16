import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.volatility import BollingerBands


class SMA_MACD_BB_Long:
    def __init__(
        self,
        df: pd.DataFrame,
        last_price: float = None,
        # Parametros SMA
        sma_window: int = 100,
        # Parametros para Bandas de Bollinger
        bb1_window: int = 20,
        bb1_dev: float = 2.0,
        bb2_window: int = 20,
        bb2_dev: float = 1.0,
        # Parametros para MACD
        macd_fast: int = 10,
        macd_slow: int = 20,
        macd_signal: int = 10,
        # Parámetros para gestion de riesgo
        dist_min: float = 0.5,         # % 0 - 1 Distancia mínima entre el precio de entrada y el stop loss
        sep_min: int = 25            # % de 0 - 100 ampliación de dist entre min_price y precio de entrada
    ):
        self.df = df.copy().reset_index(drop=True)
        self.df2 = df.copy()
        self.sma_window = sma_window
        self.bb1_window = bb1_window
        self.bb1_dev = bb1_dev
        self.bb2_window = bb2_window
        self.bb2_dev = bb2_dev
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.dist_min = dist_min
        self.sep_min = sep_min

        self._calcular_indicadores(self.df)
        self._calcular_indicadores(self.df2)
        self.last_price = last_price

        # Mostrar el DataFrame con indicadores al inicializar la clase
        #print("\n📊 DataFrame dinamico con indicadores calculados:")
        #print(self.df[["Close", "sma", "bb1_lower", "bb2_upper", "macd_line", "macd_signal"]].tail(5).to_string(index=True))
        #print(self.df2[["Close", "sma", "bb1_lower", "bb2_upper", "macd_line", "macd_signal"]].tail(5).to_string(index=True))

    def _calcular_indicadores(self, df: pd.DataFrame = None):
        close = df['Close']

        df['sma'] = SMAIndicator(close, window=self.sma_window).sma_indicator()

        bb1 = BollingerBands(close, window=self.bb1_window, window_dev=self.bb1_dev)
        df['bb1_lower'] = bb1.bollinger_lband()

        bb2 = BollingerBands(close, window=self.bb2_window, window_dev=self.bb2_dev)
        df['bb2_upper'] = bb2.bollinger_hband()

        macd = MACD(close, window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        df['macd_line'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()

    def evaluar_entrada(self):
        df = self.df
        n = len(df)
        bb1 = self.bb1_window
        bb2 = self.bb2_window
        last_price = self.last_price

        for i in range(max(bb1, bb2, self.sma_window), n - 1):
            
            # Validación de estructura - BB inferior > SMA
            if not df['bb1_lower'][i - 1] >= df['sma'][i - 1]:
                #return
                continue
            #print("✅ Señal 1: BB inferior está por encima de SMA")

            # Validación de cruce MACD
            if not (df['macd_line'][i - 1] < df['macd_signal'][i - 1] and df['macd_line'][i] > df['macd_signal'][i]):
                #return
                continue
            print("✅✅ Señal 2: Cruce MACD detectado")

            # Validación de ruptura por encima de la BB superior usando last_price
            indice_actual = len(df) - 1
            if i < indice_actual <= i + bb1:
                df_temp = df.copy()
                #df_temp = df_temp.append(df_temp.iloc[-1], ignore_index=True)
                df_temp = pd.concat([df_temp, df_temp.iloc[[-1]]], ignore_index=True)
                df_temp.at[len(df_temp) - 1, 'Close'] = last_price

                close_temp = df_temp['Close']
                bb2_recalc = BollingerBands(close_temp, window=self.bb2_window, window_dev=self.bb2_dev)
                nueva_bb2_superior = bb2_recalc.bollinger_hband().iloc[-1]

                print(f"🔍 last_price={last_price} vs nueva BB superior={nueva_bb2_superior}")

                if last_price > nueva_bb2_superior:
                    min_price = df['Low'][i - bb2:i].min()
                    dist_pct = abs((last_price - min_price) / min_price) * 100

                if dist_pct < self.dist_min:
                    continue
                else:
                    stop_loss = last_price - abs(last_price - min_price) * (1 + self.sep_min / 100)
                    print("✅✅✅ Señal 3: Ruptura dinámica confirmada con precio actual")
                    return {
                        "precio_entrada": last_price,
                        "stop_loss": stop_loss,
                        "estrategia_valida": True
                    }

        return {"estrategia_valida": False}


class SMA_MACD_BB_Long2:
    def __init__(
        self,
        df: pd.DataFrame,
        last_price: float = None,
        # Variables de configuración:
        sma_window: int = 100,
        bb1_window: int = 20,
        bb1_dev: float = 2.0,
        bb2_window: int = 20,
        bb2_dev: float = 1,
        macd_fast: int = 10,
        macd_slow: int = 20,
        macd_signal: int = 10
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
        self.last_price = last_price

    def _calcular_indicadores(self):
        close = self.df['Close']

        self.df['sma'] = SMAIndicator(close, window=self.sma_window).sma_indicator()

        bb1 = BollingerBands(close, window=self.bb1_window, window_dev=self.bb1_dev)
        self.df['bb1_lower'] = bb1.bollinger_lband()

        bb2 = BollingerBands(close, window=self.bb2_window, window_dev=self.bb2_dev)
        self.df['bb2_upper'] = bb2.bollinger_hband()

        macd = MACD(close, window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        self.df['macd_line'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()

    def evaluar_entrada(self,):
        df = self.df
        n = len(df)
        bb1 = self.bb1_window
        bb2 = self.bb2_window

        for i in range(max(bb1, self.bb2_window, self.sma_window), n):

            # Validación de estructura - BB inferior > SMA
            if df['bb1_lower'][i - 1] <= df['sma'][i - 1]:
                continue
            print("Media movil simple por debajo de la banda inferior de Bollinger")

            # Validación de cruce MACD
            if not (df['macd_line'][i - 1] < df['macd_signal'][i - 1] and df['macd_line'][i] > df['macd_signal'][i]):
                continue
            print("Cruce MACD válido")

            # Confirmación en las siguientes bb1 velas usando last_price
            for j in range(i + 1, i + bb1 + 1):
                if j >= n:
                    break

                if self.last_price > df['bb2_upper'][j]:
                    stop_loss = df['low'][i - bb2:i].min()
                    return {
                        "precio_entrada": self.last_price,
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