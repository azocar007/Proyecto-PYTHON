### MODOS DE GESTION OPERATIVA ###
import pprint
import datetime as dt
import numpy as np
import pandas as pd
import os
import psutil
import threading
import calendar, time
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR

# Funciones anidades a la funciones LONG, SHORT y SNOW BALL para la gestión de volumen
def gest_porcen_reentradas(monedas, porcentaje_vol):
    monedas = (monedas * (porcentaje_vol/100 + 1))
    return monedas

def gest_martingala(vol_monedas, porcentaje_vol):
    monedas = sum(vol_monedas) * (porcentaje_vol/100 + 1)
    return monedas

def gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, modo_gest):
    if modo_gest == "UNIDIRECCIONAL LONG":
        monedas = abs((precio * (porcentaje_vol / 100 + 1) * sum(vol_monedas) - sum(vol_usdt)) / (precio * porcentaje_vol / 100))
    
    elif modo_gest == "UNIDIRECCIONAL SHORT":
        monedas = abs((precio * (1 - porcentaje_vol / 100) * sum(vol_monedas) - sum(vol_usdt)) / (precio * porcentaje_vol / 100))
    
    else:
        monedas = vol_usdt / precio
    
    return monedas

# Adapta el valor al múltiplo de pips de la moneda del exchange sea para el precio o el volumen de monedas
def redondeo(valor: float, pip_valor: str) -> float:
    valor_str = str(valor)
    pip_str = str(pip_valor)
    valor_decimal = Decimal(valor_str)  # Convierte float a string antes de Decimal
    pip_decimal = Decimal(pip_str)
    valor_final = valor_decimal.quantize(pip_decimal, rounding=ROUND_FLOOR)
    return float(valor_final)

# Convierte una lista de velas a un DataFrame de pandas
def conv_pdataframe(velas: list) -> pd.DataFrame:
    if not velas:
        raise ValueError("❌ La lista de velas está vacía.")

    key_maps = [
        {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'time': 'Time'},
        {'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume', 'T': 'Time'},
    ]
    
    key_sets = [set(m.keys()) for m in key_maps]

    # Eliminar encabezados o dicts inválidos
    while velas and (
        not isinstance(velas[0], dict)
        or not any(key_set.issubset(set(velas[0].keys())) for key_set in key_sets)
    ):
        velas = velas[1:]

    if not velas:
        raise ValueError("❌ No hay datos válidos tipo vela en la lista.")

    selected_map = None
    for key_map in key_maps:
        if all(k in velas[0] for k in key_map.keys()):
            selected_map = key_map
            break

    if not selected_map:
        raise ValueError(f"⚠️ No se reconoce el formato de las velas. Claves encontradas: {list(velas[0].keys())}")

    if not all(all(k in v for k in selected_map.keys()) for v in velas):
        raise ValueError("⚠️ La lista contiene elementos inconsistentes con el formato detectado.")

    df = pd.DataFrame(velas)
    df.rename(columns=selected_map, inplace=True)
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df.set_index('Time', inplace=True)
    df.sort_index(inplace=True)
    df["Avg_price"] = df[["Close", "Open", "High", "Low"]].mean(axis=1)

    return df

# Metodo para convertir el argumento de la temporalidad a segundos
def temporalidad_a_segundos(temporalidad: str = None) -> int:
    unidades = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    valor = int(temporalidad[:-1])
    unidad = temporalidad[-1]
    return valor * unidades.get(unidad, 60)

# mantiene self.df siempre actualizado
def df_dynamic_start(bot):

    def sync_loop():
        print("🧠 Hilo de actualización de actualización de DataFrame dinamico")
        while True:
            seconds = temporalidad_a_segundos(bot.temporalidad)
            now = time.time()
            if bot.df is None or (now - bot.last_df_update > seconds):
                raw = bot.get_last_candles(bot.symbol, bot.temporalidad, bot.cant_candles)
                #pprint.pprint(raw)
                bot.df = conv_pdataframe(raw)
                t = bot.df.index[-1].to_pydatetime()
                bot.last_df_update = calendar.timegm(t.utctimetuple())
                print(f"\n✅ Última vela cerrada (UTC): {t}")
                print(f"🕓 Epoch actual UTC: {dt.datetime.fromtimestamp(now)} | Última actualización Local: {dt.datetime.fromtimestamp(bot.last_df_update)}")

            time.sleep(1)

    #if not hasattr(bot, "df_thread") or not bot.df_thread.is_alive():
    if not isinstance(getattr(bot, "df_thread", None), threading.Thread) or not bot.df_thread.is_alive():
        bot.df_thread = threading.Thread(target=sync_loop)
        bot.df_thread.daemon = True
        bot.df_thread.start()

# te da el df actualizado al instante
def df_dynamic_pull(bot):

    seconds = temporalidad_a_segundos(bot.temporalidad)
    now = time.time()

    if bot.df is None or (now - bot.last_df_update > seconds):
        raw = bot.get_last_candles(bot.symbol, bot.temporalidad, bot.cant_candles)
        bot.df = conv_pdataframe(raw)
        t = bot.df.index[-1].to_pydatetime()
        bot.last_df_update = calendar.timegm(t.utctimetuple())

    return bot.df

""" Metodos para monitoraer el uso de memoria del proceso """

class Monitor_Memoria:

    def __init__(self, segundos_monitoreo: int = 10):
        self.segundos_monitoreo = segundos_monitoreo
        self._detener_monitor = threading.Event()
        self._hilo_monitor = None

    def _monitor_memoria(self):
        proceso = psutil.Process(os.getpid())
        while not self._detener_monitor.is_set():
            memoria = proceso.memory_info().rss / 1024 / 1024
            print(f"\n[MONITOR] Memoria usada: {memoria:.2f} MB\n")
            time.sleep(self.segundos_monitoreo)

    def iniciar(self):
        self._hilo_monitor = threading.Thread(target=self._monitor_memoria, daemon=True)
        self._hilo_monitor.start()

    def detener(self):
        self._detener_monitor.set()
        self._hilo_monitor.join()


""" CLASES PARA GESTION DE RIESGO POR DIRECCION DE MERCADO"""

# Clase para la gestión de posiciones LONG
class PosicionLong:

    # Metodo de recompras
    def recompras(self,
        precio: float,
        monto_sl: float,
        cant_ree: int,
        porcentaje_ree: float,
        monedas: float,
        porcentaje_vol: int = 0,
        cantidad_usdt_long: float = None,
        gestion_volumen: str = "MARTINGALA" # "% DE REENTRADAS", "MARTINGALA", "AGRESIVO"
        ):

        # Definiendo el valor N/A de monedas
        if monedas == "N/A":
            monedas = cantidad_usdt_long / precio

        # Definiendo valores iniciales de las listas
        list_reentradas = [precio]
        vol_monedas = [monedas]
        vol_usdt = [round(precio * monedas, 4)]
        precios_prom = []
        precios_stop_loss = []
        precio_sl = precio - monto_sl / monedas

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        i = 0
        if cant_ree <= 0:
            cant_ree = 1000

        # Bucle para obtener las listas
        while i < cant_ree and precio_sl < precio:
            # Iterador
            i += 1
            # Reentradas:
            precio = precio - (precio * porcentaje_ree/100)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, porcentaje_vol)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, porcentaje_vol)
            else:
                monedas = gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, "UNIDIRECCIONAL LONG")
            # Precios_prom (precios promedios)
            usdt = round(monedas * precio, 4)
            prom = sum(vol_usdt) / sum(vol_monedas)
            # Precio de Stop Loss
            precio_sl = prom - monto_sl / sum(vol_monedas)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt.append(usdt)
            vol_monedas.append(monedas)
            list_reentradas.append(precio)
            precios_prom.append(prom)
            precios_stop_loss.append(precio_sl)
        # Eliminando elementos que sobran en las listas
        vol_monedas.pop()
        list_reentradas.pop()
        vol_monedas.pop(0)
        list_reentradas.pop(0)
        vol_usdt.pop(0)
        precios_prom.pop(0)
        precios_stop_loss.pop(0)
        # Resultados totales
        vol_acum = sum(vol_monedas)
        vol_usdt_total = vol_acum * precios_prom[-1]
        if (cant_ree + 1) > len(list_reentradas):
            mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
        else:
            mensj = "Cantidad de entradas acorde a lo establecido"
        # Retorno de resultados
        return {"modo_gest": "UNIDIRECCIONAL LONG",
                "positionside": "LONG",
                "gestion de volumen": gestion_volumen,
                "type": "LIMIT",
                "prices": list_reentradas,
                "precios promedios": precios_prom,
                "precios de stop loss": precios_stop_loss,
                "precio de stop loss": precios_stop_loss[-1],
                "quantitys": vol_monedas,
                "volumen monedas total": vol_acum,
                "volumen USDT total": vol_usdt_total,
                "mensaje": mensj}

    # Metodo de Snow ball
    def snow_ball(self,
        precio_long: float,
        monto_sl: float,
        cant_ree: int,
        porcentaje_ree: float,
        monedas: float,
        porcentaje_vol: int = 0,
        cantidad_usdt_long: float = None,
        gestion_volumen: str = "MARTINGALA" # "% DE REENTRADAS", "MARTINGALA", "AGRESIVO"
        ):

        # Definiendo el valor N/A de monedas
        if monedas == "N/A":
            monedas = cantidad_usdt_long / precio_long 

        # Listas iniciales
        list_reent_long: list = [precio_long]
        vol_monedas = [monedas]
        vol_usdt_long = [round(precio_long * monedas, 4)]
        precios_prom_long = []
        precios_stop_loss_long = []
        precio_sl_long = precio_long - monto_sl / monedas

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        i = 0
        if cant_ree <= 2:
            cant_ree = 2

        # Bucle para obtener las listas LONG
        while i < cant_ree:
            # Iterador
            i += 1
            # Reentradas:
            precio_long = precio_long + (precio_long * porcentaje_ree / 100)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, porcentaje_vol)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, porcentaje_vol)
            else:
                monedas = gest_agresivo(precio_long, porcentaje_vol, vol_monedas, vol_usdt_long, "UNIDIRECCIONAL SHORT")
            # Precios_prom (precios promedios)
            usdt_long = round(monedas * precio_long, 4)
            prom_long = sum(vol_usdt_long) / sum(vol_monedas)
            # Precio de Stop Loss
            precio_sl_long = prom_long - monto_sl / sum(vol_monedas)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt_long.append(usdt_long)
            vol_monedas.append(monedas)
            list_reent_long.append(precio_long)
            precios_prom_long.append(prom_long)
            precios_stop_loss_long.append(precio_sl_long)
        # Eliminando elementos que sobran en las listas
        vol_monedas.pop()
        list_reent_long.pop()
        vol_monedas.pop(0)
        list_reent_long.pop(0)
        vol_usdt_long.pop(0)
        precios_prom_long.pop(0)
        precios_stop_loss_long.pop(0)
        # Resultados totales
        vol_acum = sum(vol_monedas)

        return {"modo_gest": "SNOW BALL",
                "positionside": "LONG",
                "Precios de reentradas" : list_reent_long,
                "Precios promedios" : precios_prom_long,
                "Precios de stop loss" : precios_stop_loss_long,
                "Volumenes de monedas" : vol_monedas,
                "Volumen monedas total" : vol_acum}

    # Metodo de stop loss
    def stop_loss(self, precio_prom: float, monto_sl: float, cantidad_monedas: float):
        precio_sl = precio_prom - monto_sl / cantidad_monedas
        return precio_sl

    # Metodo de take profit
    def take_profit(self, gestion_take_profit: str, precio_prom: float, monto_sl: float, cantidad_monedas: float, ratio: float):
        if gestion_take_profit == "% TAKE PROFIT":
            precio_tp = precio_prom * ratio/100 + precio_prom
            return precio_tp

        elif gestion_take_profit == "RATIO BENEFICIO/PERDIDA":
            precio_tp = abs(precio_prom - self.stop_loss(precio_prom, monto_sl, cantidad_monedas)) * ratio + precio_prom
            return precio_tp

        else: # "LCD (Carga y Descarga)"
            pass

    # Funcion para calcular el volumen de las monedas
    def vol_monedas(self, monto_sl: float, entrada_long: float, entrada_stoploss: float):
        cantidad_monedas_long = monto_sl / abs(entrada_long - entrada_stoploss)
        return cantidad_monedas_long


# Clase para la gestión de posiciones SHORT
class PosicionShort:

    # Metodo de recompras
    def recompras(self,
        precio: float,
        monto_sl: float,
        cant_ree: int,
        porcentaje_ree: float,
        monedas: float,
        porcentaje_vol: int = 0,
        cantidad_usdt_short: float = None,
        gestion_volumen: str = "MARTINGALA" # "% DE REENTRADAS", "MARTINGALA", "AGRESIVO"
        ):

        # Definiendo el valor N/A de monedas
        if monedas == "N/A":
            monedas = cantidad_usdt_short / precio

        # Definiendo valores iniciales de las listas
        list_reentradas = [precio]
        vol_monedas = [monedas]
        vol_usdt = [round(precio*monedas,4)]
        precios_prom = []
        precios_stop_loss = []
        precio_sl = (precio + monto_sl / monedas)

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        i = 0
        if cant_ree <= 0:
            cant_ree = 1000

        # Bucle para obtener las listas
        while i < cant_ree and precio_sl > precio:
            # Iterador
            i += 1
            # Reentradas:
            precio = (precio + (precio * porcentaje_ree/100))
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, porcentaje_vol)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, porcentaje_vol)
            else:
                monedas = gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, "UNIDIRECCIONAL SHORT")
            # Precios_prom (precios promedios)
            usdt = round(monedas * precio, 4)
            prom = sum(vol_usdt) / sum(vol_monedas)
            # Precio de Stop Loss
            precio_sl = prom + monto_sl / sum(vol_monedas)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt.append(usdt)
            vol_monedas.append(monedas)
            list_reentradas.append(precio)
            precios_prom.append(prom)
            precios_stop_loss.append(precio_sl)
        # Eliminando elementos que sobran en las listas
        vol_monedas.pop()
        list_reentradas.pop()
        vol_monedas.pop(0)
        list_reentradas.pop(0)
        vol_usdt.pop(0)
        precios_prom.pop(0)
        precios_stop_loss.pop(0)
        # Resultados totales
        vol_acum = sum(vol_monedas)
        vol_usdt_total = vol_acum * precios_prom[-1]
        if (cant_ree + 1) > len(list_reentradas):
            mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
        else:
            mensj = "Cantidad de entradas acorde a lo establecido"
        # Retorno de resultados
        return {"modo_gest": "UNIDIRECCIONAL SHORT",
                "positionSide": "SHORT",
                "gestion de volumen": gestion_volumen,
                "type": "LIMIT",
                "prices": list_reentradas,
                "Precios promedios": precios_prom,
                "Precios de stop loss": precios_stop_loss,
                "Precio de stop loss": precios_stop_loss[-1],
                "quantitys": vol_monedas,
                "Volumen monedas total": vol_acum,
                "Volumen USDT total": vol_usdt_total,
                "Mensaje": mensj}

    # Metodo de Snow ball
    def snow_ball(self,
        precio_short: float,
        monto_sl: float,
        cant_ree: int,
        porcentaje_ree: float,
        monedas: float,
        porcentaje_vol: int = 0,
        cantidad_usdt_short: float = None,
        gestion_volumen: str = "MARTINGALA" # "% DE REENTRADAS", "MARTINGALA", "AGRESIVO"
        ):

        if monedas == "N/A":
            monedas = cantidad_usdt_short / precio_short

        # Listas iniciales
        list_reent_short: list = [precio_short]
        vol_monedas = [monedas]
        vol_usdt_short = [round(precio_short * monedas, 4)]
        precios_prom_short = []
        precios_stop_loss_short = []
        precio_sl_short = precio_short - monto_sl / monedas

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        i = 0
        if cant_ree <= 2:
            cant_ree = 2

        # Bucle para obtener las listas SHORT
        while i < cant_ree:
            # Iterador
            i += 1
            # Reentradas:
            precio_short = precio_short - (precio_short * porcentaje_ree / 100)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, porcentaje_vol)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, porcentaje_vol)
            else:
                monedas = gest_agresivo(precio_short, porcentaje_vol, vol_monedas, vol_usdt_short, "UNIDIRECCIONAL SHORT")
            # Precios_prom (precios promedios)
            usdt_short = round(monedas * precio_short, 4)
            prom_short = sum(vol_usdt_short) / sum(vol_monedas)
            # Precio de Stop Loss
            precio_sl_short = prom_short + monto_sl / sum(vol_monedas)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt_short.append(usdt_short)
            vol_monedas.append(monedas)
            list_reent_short.append(precio_short)
            precios_prom_short.append(prom_short)
            precios_stop_loss_short.append(precio_sl_short)
        # Eliminando elementos que sobran en las listas
        vol_monedas.pop()
        list_reent_short.pop()
        vol_monedas.pop(0)
        list_reent_short.pop(0)
        vol_usdt_short.pop(0)
        precios_prom_short.pop(0)
        precios_stop_loss_short.pop(0)
        # Resultados totales        
        vol_acum = sum(vol_monedas)

        return {"modo_gest": "SNOW BALL",
                "positionSide": "SHORT",
                "Precios de reentradas" : list_reent_short,
                "Precios promedios" : precios_prom_short,
                "Precios de stop loss" : precios_stop_loss_short,
                "Volumenes de monedas" : vol_monedas,
                "Volumen monedas total" : vol_acum}

    # Metodo de stop loss
    def stop_loss(self, precio_prom: float, monto_sl: float, cantidad_monedas: float):
        precio_sl = precio_prom + monto_sl / cantidad_monedas
        return precio_sl

    # Metodo de take profit
    def take_profit(self, gestion_take_profit: str, precio_prom: float, monto_sl: float, cantidad_monedas: float, ratio: float):
        if gestion_take_profit == "% TAKE PROFIT":
            precio_tp = precio_prom - precio_prom * ratio/100
            return precio_tp

        elif gestion_take_profit == "RATIO BENEFICIO/PERDIDA":
            precio_tp = precio_prom - abs(precio_prom - self.stop_loss(precio_prom, monto_sl, cantidad_monedas)) * ratio
            return precio_tp

        else: # "LCD (Carga y Descarga)"
            pass

    # Funcion para calcular el volumen de las monedas
    def vol_monedas(self, monto_sl: float, entrada_short: float, entrada_stoploss: float):
        cantidad_monedas_short = monto_sl / abs(entrada_short - entrada_stoploss)
        return cantidad_monedas_short


# COMPROBACIÓN DEL MODULO
if __name__ == "__main__":
    #""" # Diccionario de ensayo para comprobación sin la función entrada_de_datos
    datos_de_entrada = {
                "gestion_seleccionada": "UNIDERECCIONAL SHORT" , # UNIDIRECCIONAL SHORT LONG - DOBLE TAP - SNOW BALL
                "gestion_de_entrada": "LIMITE", # MERCADO - LIMITE - BBO
                "entrada_long": 0.16421,
                "entrada_short": 0.16481,
                "porcentaje_dist_reentradas": 2,
                "cantidad_usdt_long" : 6.71,
                "cantidad_usdt_short" : 6.71,
                "cantidad_monedas_long": 40,
                "cantidad_monedas_short": 40,
                "modo_seleccionado": "% DE REENTRADAS", # % DE REENTRADAS - MARTINGALA - AGRESIVO
                "porcentaje_vol_reentrada": 50,
                "monto_de_sl": 1.0,
                "entrada_stoploss": 0.2400,
                "cantidad_de_reentradas": 4,
                "cantidad_decimales_monedas": 0,
                "cantidad_decimales_precio": 5,
                "valor_pips": "0.00001",
                "gestion_take_profit": "RATIO BENEFICIO/PERDIDA", # "% TAKE PROFIT" - "LCD (Carga y Descarga)"
                "ratio": 2
                }
    
    PosLong = PosicionLong()
    pprint.pprint(PosLong.recompras(
                                    precio = 0.16421,
                                    monto_sl = 10.0,
                                    cant_ree = 10,
                                    porcentaje_ree = 2,
                                    monedas = "N/A",
                                    cantidad_usdt_long = 6.71,
                                    porcentaje_vol = 50,
                                    gestion_volumen = "% DE REENTRADAS",
                                    ))
    #pprint.pprint(Datos_calculados_long.vol_monedas())
    #pprint.pprint(Datos_calculados_long.take_profit())
    #pprint.pprint(Datos_calculados_long.stop_loss())
    pprint.pprint(PosLong.snow_ball(
                                    precio_long = 0.16421,
                                    monto_sl = 10.0,
                                    cant_ree = 10,
                                    porcentaje_ree = 2,
                                    monedas = "N/A",
                                    cantidad_usdt_long = 6.71,
                                    porcentaje_vol = 50,
                                    gestion_volumen = "% DE REENTRADAS",
                                    ))

