import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.volatility import BollingerBands


""" === Funciones de condición reutilizables === """

def dist_valida_sl(last_price, ref_price, dist_min, sep_min, direccion='long'):
    #dist_valida = False
    stop_loss = None

    dist_pct = abs((last_price - ref_price) / ref_price) * 100
    if dist_pct >= dist_min:
        #dist_valida = True
        delta = abs(last_price - ref_price) * (1 + sep_min / 100)
        if direccion == 'long':
            stop_loss = last_price - delta
        else: # direccion == 'short'
            stop_loss = last_price + delta
    #return {"dist_valida": dist_valida, "stop_loss", stop_loss}
    return stop_loss

"""=== Clase estrategia Media Movil + MACD + Bandas de Bollinger ==="""
class SMA_MACD_BB:
    def __init__(
        self,
        df: pd.DataFrame,
        last_price: float = None,
        decimales: int = None,
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
        self.last_price = last_price
        self.decimales = decimales
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

        # Redondear los valores a los decimales especificados
        if self.decimales is not None:
            for col in ['Close', 'sma', 'bb_lower', 'bb_upper', 'macd', 'macd_signal']:
                self.df[col] = self.df[col].round(self.decimales)
                self.df2[col] = self.df2[col].round(self.decimales)

        # Mostrar el DataFrame con indicadores al inicializar la clase
        print("\n📊 DataFrame dinamico con indicadores calculados:")
        print(self.df2[["Close", "sma", "bb1_lower", "bb1_upper", "bb2_upper", "bb2_lower", "macd_line", "macd_signal"]].tail(5).to_string(index=True))

    def _calcular_indicadores(self, df: pd.DataFrame = None):
        valorsma = df['Close']
        #valorsma = df['Avg_price']

        # calculo de la media movil simple (SMA)
        df['sma'] = SMAIndicator(valorsma, window=self.sma_window).sma_indicator()

        # Calculo de MACD
        macd = MACD(valorsma, window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
        df['macd_line'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()

        # Calculo de las bandas de Bollinger
        valorbb1 = df['Close']
        #valorbb1 = df['Avg_price']
        #valorbb1 = df['High']
        bb1 = BollingerBands(valorbb1, window=self.bb1_window, window_dev=self.bb1_dev)
        df['bb1_upper'] = bb1.bollinger_hband()

        bb1 = BollingerBands(valorbb1, window=self.bb1_window, window_dev=self.bb1_dev)
        df['bb1_lower'] = bb1.bollinger_lband()

        valorbb2 = df['Close']
        #valorbb2 = df['Avg_price']
        #valorbb2 = df['Low']
        bb2 = BollingerBands(valorbb2, window=self.bb2_window, window_dev=self.bb2_dev)
        df['bb2_upper'] = bb2.bollinger_hband()

        bb2 = BollingerBands(valorbb2, window=self.bb1_window, window_dev=self.bb1_dev)
        df['bb1_lower'] = bb2.bollinger_hband()

    def evaluar_entrada_long(self):
        df = self.df
        n = len(df) -1
        bb1 = self.bb1_window
        bb2 = self.bb2_window
        last_price = self.last_price

        for i in range(max(bb1, bb2, self.sma_window), n - 1):
            
            # Validación de estructura - BB inferior > SMA
            if df['bb1_lower'][i] >= df['sma'][i]:
                #print("✅ Señal 1: BB inferior está por encima de SMA")
                #señal_1 = True
                continue

            # Validación de cruce MACD
            if (df['macd_line'][i - 1] < df['macd_signal'][i - 1] and df['macd_line'][i] > df['macd_signal'][i]):
                print("✅✅ Señal 2: Cruce MACD detectado")
                #señal_2 = True
                continue

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
                    min_price = df['Low'].iloc[i - bb2:i].min()
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

"""=== Clase estrategia Media Movil + Bandas de bollinger ==="""
class SMA_BB:
    def __init__(
        self,
        df: pd.DataFrame,
        last_price: float = None,
        decimales: float = None,
        # Parametros SMA
        sma_window: int = 300,
        # Parametros para Bandas de Bollinger
        bb_window: int = 20,
        bb_dev: float = 2.0,
        # Parámetros para gestion de riesgo
        dist_min: float = 0.5,       # % 0 - 1 Distancia mínima entre el precio de entrada y el stop loss
        sep_sl: int = 25            # % de 0 - 100 ampliación de dist entre min_price y precio de entrada
    ):
        self.last_price = last_price
        self.decimales = decimales
        self.df = df.copy().reset_index(drop=True)
        self.df2 = df.copy()
        self.sma_window = sma_window
        self.bb_window = bb_window
        self.bb_dev = bb_dev
        self.dist_min = dist_min
        self.sep_sl = sep_sl

        self._calcular_indicadores(self.df)
        self._calcular_indicadores(self.df2)
        self.condicion_1 = False
        self.condicion_2 = False

        # Redondear los valores a los decimales especificados
        if self.decimales is not None:
            for col in ['Close', 'sma', 'bb_lower', 'bb_middle', 'bb_upper']:
                self.df[col] = self.df[col].round(self.decimales)
                self.df2[col] = self.df2[col].round(self.decimales)

        # Mostrar el DataFrame con indicadores al inicializar la clase
        print("\n📊 DataFrame dinamico con indicadores calculados hasta ultima vela cerrada:")
        print(self.df2[["Close", "sma", "bb_lower", "bb_middle", "bb_upper"]].tail(5).to_string(index=True))

    def _calcular_indicadores(self, df: pd.DataFrame = None):

        # Calculo de la media movil simple (SMA)
        close = df['Close']
        #close = df['Avg_price']
        df['sma'] = SMAIndicator(close, window=self.sma_window).sma_indicator()

        # Calculo de las bandas de Bollinger

        # Banda inferior
        low = df["Close"]
        #low = df["Low"]
        bb_lower = BollingerBands(low, window=self.bb_window, window_dev=self.bb_dev)
        df['bb_lower'] = bb_lower.bollinger_lband()

        # Banda media
        bb_middle = BollingerBands(close, window=self.bb_window, window_dev=self.bb_dev)
        df['bb_middle'] = bb_middle.bollinger_mavg()

        # Banda superior
        high = df["Close"]
        #high = df["High"]
        bb_upper = BollingerBands(high, window=self.bb_window, window_dev=self.bb_dev)
        df['bb_upper'] = bb_upper.bollinger_hband()

    def evaluar_entrada_long(self):
        # Asignando valores a variables
        df = self.df
        df2 = self.df2
        i = len(df) - 1
        last_price = self.last_price
        last_printed = None

        # Validación de estructura - BB inferior > SMA
        if df['bb_lower'].iloc[i] >= df['sma'].iloc[i]:
            self.condicion_1 = True
            df2 = df2.reset_index()
            print(f"✅ Señal 1: hora: {df2['Time'].iloc[i]} BB inferior {df['bb_lower'].iloc[i]} está por encima de SMA {df['sma'].iloc[i]}")
            return {"estrategia_valida": False}

        # Calculo de la ultima Banda de bollinger inferior
        df_temp = pd.concat([self.df, self.df.iloc[[-1]]], ignore_index=True)
        df_temp.at[len(df_temp) - 1, 'Close'] = self.last_price
        bb_temp = BollingerBands(df_temp['Close'], window=self.bb_window, window_dev=self.bb_dev)
        bb_lower = round(bb_temp.bollinger_lband().iloc[-1], self.decimales)

        current = (last_price, bb_lower)
        if last_printed != current:
            print(f"🔍 last_price= {last_price} vs nueva BB inferior = {bb_lower}")
            last_printed = current

        if last_price <= bb_lower and self.condicion_1:
            min_price = df['Low'].iloc[i - self.bb_window:i].min()
            stop_loss = dist_valida_sl(last_price, min_price, self.dist_min, self.sep_sl, 'long')
            if stop_loss is None:
                self.condicion_1 = False
                return {"estrategia_valida": False}
            else:
                self.condicion_2 = True
                print("✅✅ Señal 2: Ruptura dinámica confirmada con precio actual")
                print(f"Precio de entrada: {last_price}, Stop Loss: {stop_loss}, precio minimo: {min_price}")
                """
                return {
                        "precio_entrada": last_price,
                        "stop_loss": stop_loss,
                        "estrategia_valida": True
                        }
                """
        if self.condicion_1 and self.condicion_2:
            self.condicion_1 = False
            self.condicion_2 = False
            return {
                    "precio_entrada": last_price,
                    "stop_loss": stop_loss,
                    "estrategia_valida": False
                    }

        return {"estrategia_valida": False}