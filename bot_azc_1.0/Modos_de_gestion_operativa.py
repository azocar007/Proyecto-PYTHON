### MODOS DE GESTION OPERATIVA ###
import pprint
from Entrada_de_datos import entrada_de_datos
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
        vol_acum = sum(vol_monedas)
        vol_usdt_total = vol_acum * precios_prom[-1]
        if cant_ree > len(list_reentradas):
            mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
        else:
            mensj = "Cantidad de entradas acorde a lo establecido"
        # Retorno de resultados
        return {"modo_gest": "UNIDIRECCIONAL LONG",
                "positionside": "LONG",
                "gestion de volumen": gestion_volumen,
                "type": "LIMIT",
                "Prices": list_reentradas,
                "Precios promedios": precios_prom,
                "Precios de stop loss": precios_stop_loss,
                "Precio de stop loss": precios_stop_loss[-1],
                "quantitys": vol_monedas,
                "Volumen monedas total": vol_acum,
                "Volumen USDT total": vol_usdt_total,
                "Mensaje": mensj}

    # Metodo de Snow ball
    def snow_ball(self,
        precio_long: float,
        monedas: float,
        cant_ree: int,
        monto_sl: float,
        porcentaje_ree: float,
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
        vol_monedas.pop()
        list_reent_long.pop()
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
        vol_acum = sum(vol_monedas)
        vol_usdt_total = vol_acum * precios_prom[-1]
        if cant_ree > len(list_reentradas):
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
        monedas: float,
        cant_ree: int,
        monto_sl: float,
        porcentaje_ree: float,
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
        vol_monedas.pop()
        list_reent_short.pop()
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
    #"""
    # Empleando el modulo Entrada_de_datos

    #Datos_calculados = PosicionLong(entrada_de_datos())
    #Datos_calculados = PosicionShort(entrada_de_datos())

    # Empleando el diccionario de ensayo

    # Long
    """
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
    """

    # Short
    """
    PosShort = PosicionShort()
    pprint.pprint(PosShort.recompras(
                                    precio = 0.16421,
                                    monto_sl = 10.0,
                                    cant_ree = 3,
                                    porcentaje_ree = 2,
                                    monedas = "N/A",
                                    cantidad_usdt_short = 6.71,
                                    porcentaje_vol = 50,
                                    gestion_volumen = "% DE REENTRADAS",
                                    ))
    #pprint.pprint(Datos_calculados_short.vol_monedas())
    #pprint.pprint(Datos_calculados_short.take_profit())
    #pprint.pprint(Datos_calculados_short.stop_loss())
    pprint.pprint(PosShort.snow_ball(
                                    precio_short = 0.16421,
                                    monto_sl = 10.0,
                                    cant_ree = 3,
                                    porcentaje_ree = 2,
                                    monedas = "N/A",
                                    cantidad_usdt_short = 6.71,
                                    porcentaje_vol = 50,
                                    gestion_volumen = "% DE REENTRADAS",
                                    ))
    """

    """ 
    Para cambiar un dato de los diccionarios resultantes de la clase
    debemos cambiar el valor de la variable en el diccionario de entrada y
    volver a instanciar (ejecutar) la clase con el nuevo diccionario de entrada.
    No es necesario crear una nueva variable para igualarla con algun valor extraido 
    de los diccionarios resultantes de la clase.
        def __init__(self, entrada_de_datos: dict):
        # Variables del diccionario de entrada de datos
        self.gestion_seleccionada = entrada_de_datos["gestion_seleccionada"] # UNIDIRECCIONAL SHORT LONG - DOBLE TAP - SNOW BALL - RATIO BENEFICIO/PERDIDA
        self.gestion_de_entrada = entrada_de_datos["gestion_de_entrada"] # MERCADO - LIMITE - BBO
        self.entrada_long = entrada_de_datos["entrada_long"]
        self.entrada_short = entrada_de_datos["entrada_short"]
        self.porcentaje_dist_reentradas = entrada_de_datos["porcentaje_dist_reentradas"]
        self.cantidad_usdt_long = entrada_de_datos["cantidad_usdt_long"]
        self.cantidad_usdt_short = entrada_de_datos["cantidad_usdt_short"]
        self.cantidad_monedas_long = entrada_de_datos["cantidad_monedas_long"]
        self.cantidad_monedas_short = entrada_de_datos["cantidad_monedas_short"]
        self.modo_seleccionado = entrada_de_datos["modo_seleccionado"] # % DE REENTRADAS - MARTINGALA - AGRESIVO
        self.porcentaje_vol_reentrada = entrada_de_datos["porcentaje_vol_reentrada"]
        self.monto_de_sl = entrada_de_datos["monto_de_sl"]
        self.entrada_stoploss = entrada_de_datos["entrada_stoploss"]
        self.cantidad_de_reentradas = entrada_de_datos["cantidad_de_reentradas"]
        self.cantidad_decimales_monedas = entrada_de_datos["cantidad_decimales_monedas"] # Cantidad de decimales en las monedas
        self.cantidad_decimales_precio = entrada_de_datos["cantidad_decimales_precio"] # Cantidad de decimales en los precios
        self.valor_pips = entrada_de_datos["valor_pips"]
        self.gestion_take_profit = entrada_de_datos["gestion_take_profit"] # "% TAKE PROFIT" - "LCD (Carga y Descarga)"
        self.ratio = entrada_de_datos["ratio"]
    """

    # nueva_entrada_short = Datos_calculados_short.recompras()["Precios promedios"][-2]
    #datos_de_entrada["entrada_short"] = Datos_calculados_short.recompras()["Precios promedios"][-1] #nueva_entrada_short
    #Datos_calculados_short = PosicionShort(datos_de_entrada)

    #print("\nDatos de Snow ball SHORT:")
    #pprint.pprint(Datos_calculados_short.snow_ball())
