### MODOS DE GESTION OPERATIVA ###
import pprint
from Entrada_de_datos import entrada_de_datos
from pybit.unified_trading import HTTP
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR

# Funciones anidades a la funciones LONG, SHORT y SNOW BALL para la gestión de volumen
def gest_porcen_reentradas(monedas, porcentaje_vol, decimales_mon):
    monedas = round((monedas * (porcentaje_vol/100 + 1)), decimales_mon)
    return monedas

def gest_martingala(vol_monedas, porcentaje_vol, decimales_mon):
    monedas = round(sum(vol_monedas) * (porcentaje_vol/100 + 1), decimales_mon)
    return monedas

def gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, decimales_mon, modo_gest):
    if modo_gest == "UNIDIRECCIONAL LONG":
        monedas = round(abs((precio * (porcentaje_vol / 100 + 1) * sum(vol_monedas) - sum(vol_usdt)) / (precio * porcentaje_vol / 100)), decimales_mon)
    
    elif modo_gest == "UNIDIRECCIONAL SHORT":
        monedas = round(abs((precio * (1 - porcentaje_vol / 100) * sum(vol_monedas) - sum(vol_usdt)) / (precio * porcentaje_vol / 100)), decimales_mon)
    
    else:
        monedas = vol_usdt / precio
    
    return monedas

# FUNCIONES PARA LA GESTION DE RIESGO
# Calculos de Gestion "UNIDERECCIONAL LONG"
def cal_unidereccional_long(datos_calculados: dict):

    # Definir las variables de la función con los indices del diccionario    
    modo_gest = "UNIDIRECCIONAL LONG"
    i = 0
    precio = datos_calculados["entrada_long"]
    monedas = datos_calculados["cantidad_monedas_long"]
    monto_sl = datos_calculados["monto_de_sl"]
    decimales_pre = datos_calculados["cantidad_decimales_precio"]
    cant_ree = datos_calculados["cantidad_de_reentradas"]
    porcentaje_ree = datos_calculados["porcentaje_dist_reentradas"]
    gestion_volumen = datos_calculados["modo_seleccionado"]
    porcentaje_vol = datos_calculados["porcentaje_vol_reentrada"]
    decimales_mon = datos_calculados["cantidad_decimales_monedas"]

    # Definiendo valores iniciales de las listas
    list_reentradas = [precio]
    vol_monedas = [monedas]
    vol_usdt = [round(precio*monedas,4)]
    precios_prom = []
    precios_stop_loss = []
    precio_sl = round((precio - monto_sl / monedas), decimales_pre)

    # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
    if cant_ree <= 0:
        cant_ree = 1000

    # Bucle para obtener las listas
    while i < cant_ree and precio_sl < precio:
        # Iterador
        i += 1
        # Reentradas:
        precio = round((precio - (precio * porcentaje_ree/100)), decimales_pre)
        # vol_monedas:
        if gestion_volumen == "MARTINGALA":
            monedas = gest_martingala(vol_monedas, porcentaje_vol, decimales_mon)
        elif gestion_volumen == "% DE REENTRADAS":
            monedas = gest_porcen_reentradas(monedas, porcentaje_vol, decimales_mon)
        else:
            monedas = gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, decimales_mon, modo_gest)
        # Precios_prom (precios promedios)
        usdt = round(monedas * precio, 4)
        prom = round(sum(vol_usdt) / sum(vol_monedas), decimales_pre)
        # Precio de Stop Loss
        precio_sl = round(prom - monto_sl / sum(vol_monedas),decimales_pre)
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
    vol_usdt_total = round(vol_acum * precios_prom[-1], datos_calculados["cant_decimales_sl"])
    if cant_ree > len(list_reentradas):
        mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
    else:
        mensj = "Cantidad de entradas acorde a lo establecido"
    # Retorno de resultados
    return list_reentradas, vol_monedas, vol_acum, precios_prom, precios_stop_loss, mensj, vol_usdt_total

# Calculos de Gestion "UNIDERECCIONAL SHORT"
def cal_unidereccional_short(datos_calculados: dict):

    # Definir las variables de la función con los indices del diccionario    
    modo_gest = "UNIDIRECCIONAL SHORT"
    i = 0
    precio = datos_calculados["entrada_short"]
    monedas = datos_calculados["cantidad_monedas_short"]
    monto_sl = datos_calculados["monto_de_sl"]
    decimales_pre = datos_calculados["cantidad_decimales_precio"]
    cant_ree = datos_calculados["cantidad_de_reentradas"]
    porcentaje_ree = datos_calculados["porcentaje_dist_reentradas"]
    gestion_volumen = datos_calculados["modo_seleccionado"]
    porcentaje_vol = datos_calculados["porcentaje_vol_reentrada"]
    decimales_mon = datos_calculados["cantidad_decimales_monedas"]

    # Definiendo valores iniciales de las listas
    list_reentradas = [precio]
    vol_monedas = [monedas]
    vol_usdt = [round(precio*monedas,4)]
    precios_prom = []
    precios_stop_loss = []
    precio_sl = round((precio + monto_sl / monedas), decimales_pre)

    # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
    if cant_ree <= 0:
        cant_ree = 1000

    # Bucle para obtener las listas
    while i < cant_ree and precio_sl > precio:
        # Iterador
        i += 1
        # Reentradas:
        precio = round((precio + (precio * porcentaje_ree/100)), decimales_pre)
        # vol_monedas:
        if gestion_volumen == "MARTINGALA":
            monedas = gest_martingala(vol_monedas, porcentaje_vol, decimales_mon)
        elif gestion_volumen == "% DE REENTRADAS":
            monedas = gest_porcen_reentradas(monedas, porcentaje_vol, decimales_mon)
        else:
            monedas = gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, decimales_mon, modo_gest)
        # Precios_prom (precios promedios)
        usdt = round(monedas * precio, 4)
        prom = round(sum(vol_usdt) / sum(vol_monedas), decimales_pre)
        # Precio de Stop Loss
        precio_sl = round(prom + monto_sl / sum(vol_monedas),decimales_pre)
        # Ingreso de resultados a las listas correspondientes
        vol_usdt.append(usdt)
        vol_monedas.append(monedas)
        list_reentradas.append(precio)
        precios_prom.append(prom)
        precios_stop_loss.append(precio_sl)

    vol_monedas.pop()
    list_reentradas.pop()
    vol_acum = sum(vol_monedas)
    vol_usdt_total = round(vol_acum * precios_prom[-1], datos_calculados["cant_decimales_sl"])
    if cant_ree > len(list_reentradas):
        mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
    else:
        mensj = "Cantidad de entradas acorde a lo establecido"
    # Retorno de resultados
    return list_reentradas, vol_monedas, vol_acum, precios_prom, precios_stop_loss, mensj, vol_usdt_total

# Calculos de Gestion "SNOW BALL"
def cal_snow_ball(datos_calculados: dict):
    # Datos internos de la función
    i = 0
    precio_long = datos_calculados["entrada_long"]
    precio_short = datos_calculados["entrada_short"]
    list_reent_long = [precio_long]
    list_reent_short = [precio_short]
    monedas = datos_calculados["cantidad_monedas_long"]
    gestion_volumen = datos_calculados["modo_seleccionado"]
    vol_monedas = [monedas]
    vol_usdt_long = [round(precio_long * datos_calculados["cantidad_monedas_long"], 4)]
    vol_usdt_short = [round(precio_short * datos_calculados["cantidad_monedas_long"], 4)]
    precios_prom_long = []
    precios_prom_short = []
    precios_stop_loss_long = []
    precios_stop_loss_short = []
    precio_sl_long = round((precio_long - datos_calculados["monto_de_sl"] / datos_calculados["cantidad_monedas_long"]), datos_calculados["cantidad_decimales_precio"])
    precio_sl_short = round((precio_short + datos_calculados["monto_de_sl"] / datos_calculados["cantidad_monedas_long"]), datos_calculados["cantidad_decimales_precio"])
    decimales_mon = datos_calculados["cantidad_decimales_monedas"]

    # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
    if datos_calculados["cantidad_de_reentradas"] <= 2:
        datos_calculados["cantidad_de_reentradas"] = 2

    # Bucle para obtener las listas LONG
    while i < datos_calculados["cantidad_de_reentradas"]:
        # Iterador
        i += 1
        # Reentradas:
        precio_long = round((precio_long + (precio_long * datos_calculados["porcentaje_vol_reentrada"] / 100)), datos_calculados["cantidad_decimales_precio"])
        precio_short = round((precio_short - (precio_short * datos_calculados["porcentaje_vol_reentrada"] / 100)), datos_calculados["cantidad_decimales_precio"])
        # vol_monedas:
        if gestion_volumen == "MARTINGALA":
            monedas = gest_martingala(vol_monedas, datos_calculados["porcentaje_vol_reentrada"], datos_calculados["cantidad_decimales_monedas"])
        elif gestion_volumen == "% DE REENTRADAS":
            monedas = gest_porcen_reentradas(monedas, datos_calculados["porcentaje_vol_reentrada"], datos_calculados["cantidad_decimales_monedas"])
        else:
            monedas = gest_agresivo(precio_long, datos_calculados["porcentaje_vol_reentrada"], vol_monedas, vol_usdt_long, decimales_mon, modo_gest = "UNIDIRECCIONAL SHORT")
        # Precios_prom (precios promedios)
        usdt_long = round(monedas * precio_long, 4)
        usdt_short = round(monedas * precio_short, 4)
        prom_long = round(sum(vol_usdt_long) / sum(vol_monedas), datos_calculados["cantidad_decimales_precio"])
        prom_short = round(sum(vol_usdt_short) / sum(vol_monedas), datos_calculados["cantidad_decimales_precio"])
        # Precio de Stop Loss
        precio_sl_long = round(prom_long - datos_calculados["monto_de_sl"] / sum(vol_monedas), datos_calculados["cantidad_decimales_precio"])
        precio_sl_short = round(prom_short + datos_calculados["monto_de_sl"] / sum(vol_monedas), datos_calculados["cantidad_decimales_precio"])
        # Ingreso de resultados a las listas correspondientes
        vol_usdt_long.append(usdt_long)
        vol_usdt_short.append(usdt_short)
        vol_monedas.append(monedas)
        list_reent_long.append(precio_long)
        list_reent_short.append(precio_short)
        precios_prom_long.append(prom_long)
        precios_prom_short.append(prom_short)
        precios_stop_loss_long.append(precio_sl_long)
        precios_stop_loss_short.append(precio_sl_short)
    vol_monedas.pop()
    list_reent_long.pop()
    list_reent_short.pop()
    vol_acum = sum(vol_monedas)

    return list_reent_long, list_reent_short, vol_monedas, vol_acum, precios_prom_long, precios_prom_short, precios_stop_loss_long, precios_stop_loss_short

# Adapta el precio al múltiplo de pips de la moneda del exchange
def redondeo(precio, pip_precio):
    precio_final = Decimal(precio).quantize(pip_precio, rounding=ROUND_FLOOR)
    return float(precio_final)

# Clase para la gestión de posiciones LONG
class PosicionLong:
    # Variables de la clase
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

    # Metodo de recompras
    def recompras(self):
        # Definir las variables de la función con las claves del diccionario    
        i = 0
        modo_gest = "UNIDIRECCIONAL LONG"
        precio = self.entrada_long
        monedas = self.cantidad_monedas_long
        monto_sl = self.monto_de_sl
        decimales_pre = self.cantidad_decimales_precio
        cant_ree = self.cantidad_de_reentradas
        porcentaje_ree = self.porcentaje_dist_reentradas
        gestion_volumen = self.modo_seleccionado
        porcentaje_vol = self.porcentaje_vol_reentrada
        decimales_mon = self.cantidad_decimales_monedas

        # Definiendo el valor N/A de monedas 
        if monedas == "N/A":
            monedas = round(precio * self.cantidad_usdt_long, decimales_mon)

        # Definiendo valores iniciales de las listas
        list_reentradas = [precio]
        vol_monedas = [monedas]
        vol_usdt = [round(precio*monedas,4)]
        precios_prom = []
        precios_stop_loss = []
        precio_sl = round((precio - monto_sl / monedas), decimales_pre)

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        if cant_ree <= 0:
            cant_ree = 1000

        # Bucle para obtener las listas
        while i < cant_ree and precio_sl < precio:
            # Iterador
            i += 1
            # Reentradas:
            precio = round((precio - (precio * porcentaje_ree/100)), decimales_pre)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, porcentaje_vol, decimales_mon)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, porcentaje_vol, decimales_mon)
            else:
                monedas = gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, decimales_mon, modo_gest)
            # Precios_prom (precios promedios)
            usdt = round(monedas * precio, 4)
            prom = round(sum(vol_usdt) / sum(vol_monedas), decimales_pre)
            # Precio de Stop Loss
            precio_sl = round(prom - monto_sl / sum(vol_monedas),decimales_pre)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt.append(usdt)
            vol_monedas.append(monedas)
            list_reentradas.append(precio)
            precios_prom.append(prom)
            precios_stop_loss.append(precio_sl)
        # Eliminando elementos que sobran en las listas
        vol_monedas.pop()
        list_reentradas.pop()
        vol_acum = round(sum(vol_monedas),decimales_mon)
        vol_usdt_total = round(vol_acum * precios_prom[-1], self.cantidad_decimales_monedas)
        if cant_ree > len(list_reentradas):
            mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
        else:
            mensj = "Cantidad de entradas acorde a lo establecido"
        # Retorno de resultados
        return {"Precios de reentradas": list_reentradas,
                "Precios promedios": precios_prom,
                "Precios de stop loss": precios_stop_loss,
                "Precio de stop loss": precios_stop_loss[-1],
                "Volumenes de monedas": vol_monedas,
                "Volumen monedas total": vol_acum,
                "Volumen USDT total": vol_usdt_total,
                "Mensaje": mensj}

    # Metodo de snow ball
    def snow_ball(self):
        # Definir las variables de la función con las claves del diccionario    
        i = 0
        precio_long = self.entrada_long
        list_reent_long = [precio_long]
        monedas = self.cantidad_monedas_long
        gestion_volumen = self.modo_seleccionado
        vol_monedas = [monedas]
        vol_usdt_long = [round(precio_long * self.cantidad_monedas_long, 4)]
        precios_prom_long = []
        precios_stop_loss_long = []
        precio_sl_long = round((precio_long - self.monto_de_sl / self.cantidad_monedas_long), self.cantidad_decimales_precio)
        decimales_mon = self.cantidad_decimales_monedas

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        if self.cantidad_de_reentradas <= 2:
            self.cantidad_de_reentradas = 2

        # Bucle para obtener las listas LONG
        while i < self.cantidad_de_reentradas:
            # Iterador
            i += 1
            # Reentradas:
            precio_long = round((precio_long + (precio_long * self.porcentaje_dist_reentradas / 100)), self.cantidad_decimales_precio)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, self.porcentaje_vol_reentrada, self.cantidad_decimales_monedas)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, self.porcentaje_vol_reentrada, self.cantidad_decimales_monedas)
            else:
                monedas = gest_agresivo(precio_long, self.porcentaje_vol_reentrada, vol_monedas, vol_usdt_long, decimales_mon, modo_gest = "UNIDIRECCIONAL SHORT")
            # Precios_prom (precios promedios)
            usdt_long = round(monedas * precio_long, 4)
            prom_long = round(sum(vol_usdt_long) / sum(vol_monedas), self.cantidad_decimales_precio)
            # Precio de Stop Loss
            precio_sl_long = round(prom_long - self.monto_de_sl / sum(vol_monedas), self.cantidad_decimales_precio)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt_long.append(usdt_long)
            vol_monedas.append(monedas)
            list_reent_long.append(precio_long)
            precios_prom_long.append(prom_long)
            precios_stop_loss_long.append(precio_sl_long)
        vol_monedas.pop()
        list_reent_long.pop()
        vol_acum = sum(vol_monedas)

        return {"Precios de reentradas" : list_reent_long,
                "Precios promedios" : precios_prom_long,
                "Precios de stop loss" : precios_stop_loss_long,
                "Volumenes de monedas" : vol_monedas,
                "Volumen monedas total" : vol_acum}

    # Metodo de stop loss
    def stop_loss(self):
        """
        Se deben redefinir las variables: 
        posicion_actual = COLOCAR LA FUNCIÓN QUE LLAMA LA POSICIÓN ACTUAL DE LA OPERACIÓN EN EL ACTIVO
        monto_de_sl = self.monto_de_sl
        cantidad_monedas_actual
        cantidad_decimales_precio
        """
        precio_sl = round((self.entrada_long - self.monto_de_sl / self.cantidad_monedas_long), self.cantidad_decimales_precio)
        precio_sl = redondeo(precio_sl, self.valor_pips)
        return {"Volumen moneda total": self.cantidad_monedas_long,
                "Precio de stop loss": precio_sl}

    # Metodo de take profit
    def take_profit(self):
        """
        Se deben redefinir las variables: 
        posicion_actual = COLOCAR LA FUNCIÓN QUE LLAMA LA POSICIÓN ACTUAL DE LA OPERACIÓN EN EL ACTIVO
        monto_de_sl = self.monto_de_sl
        cantidad_monedas_actual
        cantidad_decimales_precio
        """
        if self.gestion_take_profit == "% TAKE PROFIT":
            precio_tp = round((self.entrada_long * self.ratio/100 + self.entrada_long), self.cantidad_decimales_precio)
            return {"Volumen moneda total": self.cantidad_monedas_long,
                    "Precio de take profit": precio_tp}
        elif self.gestion_take_profit == "RATIO BENEFICIO/PERDIDA":
            precio_tp = round(abs(abs(self.entrada_long - self.entrada_stoploss) * self.ratio + self.entrada_long), self.cantidad_decimales_precio)
            return {"Volumen monedas total": self.cantidad_monedas_short,
                    "Precio de take profit": precio_tp}
        else: # "LCD (Carga y Descarga)"
            pass

    # Funcion para calcular el volumen de las monedas
    def vol_monedas(self):
        if self.gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG":
            self.cantidad_monedas_long = round((self.monto_de_sl ) / abs(self.entrada_long - self.entrada_stoploss), self.cantidad_decimales_monedas)
        return {"Precio de entrada" : self.entrada_long,
                "Volumen monedas total": self.cantidad_monedas_long,
                "Precio de stop loss": self.entrada_stoploss}

# Clase para la gestión de posiciones SHORT
class PosicionShort: # Falta calcular el metodo de snow ball
    # Variables de la clase 
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

    # Metodo de recompras
    def recompras(self):
        # Definir las variables de la función con las claves del diccionario    
        i = 0
        modo_gest = "UNIDIRECCIONAL SHORT"
        precio = self.entrada_short
        monedas = self.cantidad_monedas_short
        monto_sl = self.monto_de_sl
        decimales_pre = self.cantidad_decimales_precio
        cant_ree = self.cantidad_de_reentradas
        porcentaje_ree = self.porcentaje_dist_reentradas
        gestion_volumen = self.modo_seleccionado
        porcentaje_vol = self.porcentaje_vol_reentrada
        decimales_mon = self.cantidad_decimales_monedas

        # Definiendo el valor N/A de monedas
        if monedas == "N/A":
            monedas = round(self.cantidad_usdt_short / precio, decimales_mon)

        # Definiendo valores iniciales de las listas
        list_reentradas = [precio]
        vol_monedas = [monedas]
        vol_usdt = [round(precio*monedas,4)]
        precios_prom = []
        precios_stop_loss = []
        precio_sl = round((precio + monto_sl / monedas), decimales_pre)

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        if cant_ree <= 0:
            cant_ree = 1000

        # Bucle para obtener las listas
        while i < cant_ree and precio_sl > precio:
            # Iterador
            i += 1
            # Reentradas:
            precio = round((precio + (precio * porcentaje_ree/100)), decimales_pre)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, porcentaje_vol, decimales_mon)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, porcentaje_vol, decimales_mon)
            else:
                monedas = gest_agresivo(precio, porcentaje_vol, vol_monedas, vol_usdt, decimales_mon, modo_gest)
            # Precios_prom (precios promedios)
            usdt = round(monedas * precio, 4)
            prom = round(sum(vol_usdt) / sum(vol_monedas), decimales_pre)
            # Precio de Stop Loss
            precio_sl = round(prom + monto_sl / sum(vol_monedas),decimales_pre)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt.append(usdt)
            vol_monedas.append(monedas)
            list_reentradas.append(precio)
            precios_prom.append(prom)
            precios_stop_loss.append(precio_sl)
        # Eliminando elementos que sobran en las listas
        vol_monedas.pop()
        list_reentradas.pop()
        vol_acum = round(sum(vol_monedas),decimales_mon)
        vol_usdt_total = round(vol_acum * precios_prom[-1], self.cantidad_decimales_monedas)
        if cant_ree > len(list_reentradas):
            mensj = "Cantidad de entradas solicitadas es mayor a las calculadas."
        else:
            mensj = "Cantidad de entradas acorde a lo establecido"
        # Retorno de resultados
        return {"Precios de reentradas": list_reentradas,
                "Precios promedios": precios_prom,
                "Precios de stop loss": precios_stop_loss,
                "Precio de stop loss": precios_stop_loss[-1],
                "Volumenes de monedas": vol_monedas,
                "Volumen monedas total": vol_acum,
                "Volumen USDT total": vol_usdt_total,
                "Mensaje": mensj}

    # Metodo de snow ball
    def snow_ball(self):
        # Definir las variables de la función con las claves del diccionario    
        i = 0
        precio_short = self.entrada_short
        list_reent_short = [precio_short]
        monedas = self.cantidad_monedas_short
        gestion_volumen = self.modo_seleccionado
        vol_monedas = [monedas]
        vol_usdt_short = [round(precio_short * self.cantidad_monedas_short, 4)]
        precios_prom_short = []
        precios_stop_loss_short = []
        precio_sl_short = round((precio_short + self.monto_de_sl / self.cantidad_monedas_short), self.cantidad_decimales_precio)
        decimales_mon = self.cantidad_decimales_monedas

        # Condicional para corregir el valor de "cero 0" en la cantidad de reentradas
        if self.cantidad_de_reentradas <= 2:
            self.cantidad_de_reentradas = 2

        # Bucle para obtener las listas SHORT
        while i < self.cantidad_de_reentradas:
            # Iterador
            i += 1
            # Reentradas:
            precio_short = round((precio_short - (precio_short * self.porcentaje_dist_reentradas / 100)), self.cantidad_decimales_precio)
            # vol_monedas:
            if gestion_volumen == "MARTINGALA":
                monedas = gest_martingala(vol_monedas, self.porcentaje_vol_reentrada, self.cantidad_decimales_monedas)
            elif gestion_volumen == "% DE REENTRADAS":
                monedas = gest_porcen_reentradas(monedas, self.porcentaje_vol_reentrada, self.cantidad_decimales_monedas)
            else:
                monedas = gest_agresivo(precio_short, self.porcentaje_vol_reentrada, vol_monedas, vol_usdt_short, decimales_mon, modo_gest = "UNIDIRECCIONAL SHORT")
            # Precios_prom (precios promedios)
            usdt_short = round(monedas * precio_short, 4)
            prom_short = round(sum(vol_usdt_short) / sum(vol_monedas), self.cantidad_decimales_precio)
            # Precio de Stop Loss
            precio_sl_short = round(prom_short + self.monto_de_sl / sum(vol_monedas), self.cantidad_decimales_precio)
            # Ingreso de resultados a las listas correspondientes
            vol_usdt_short.append(usdt_short)
            vol_monedas.append(monedas)
            list_reent_short.append(precio_short)
            precios_prom_short.append(prom_short)
            precios_stop_loss_short.append(precio_sl_short)
        vol_monedas.pop()
        list_reent_short.pop()
        vol_acum = sum(vol_monedas)

        return {"Precios de reentradas" : list_reent_short,
                "Precios promedios" : precios_prom_short,
                "Precios de stop loss" : precios_stop_loss_short,
                "Volumenes de monedas" : vol_monedas,
                "Volumen monedas total" : vol_acum}

    # Metodo de stop loss
    def stop_loss(self):
        """
        Se deben redefinir las variables: 
        posicion_actual = COLOCAR LA FUNCIÓN QUE LLAMA LA POSICIÓN ACTUAL DE LA OPERACIÓN EN EL ACTIVO
        monto_de_sl = self.monto_de_sl
        cantidad_monedas_actual
        cantidad_decimales_precio
        """
        precio_sl = round((self.entrada_short + self.monto_de_sl / self.cantidad_monedas_short), self.cantidad_decimales_precio)
        return {"Volumen moneda total": self.cantidad_monedas_short,
                "Precio de stop loss": precio_sl}

    # Metodo de take profit
    def take_profit(self):
        """
        Se deben redefinir las variables: 
        posicion_actual = COLOCAR LA FUNCIÓN QUE LLAMA LA POSICIÓN ACTUAL DE LA OPERACIÓN EN EL ACTIVO
        monto_de_sl = self.monto_de_sl
        cantidad_monedas_actual
        cantidad_decimales_precio
        """
        if self.gestion_take_profit == "% TAKE PROFIT":
            precio_tp = round(abs(self.entrada_short * self.ratio/100 - self.entrada_short), self.cantidad_decimales_precio)
            return {"Volumen moneda total": self.cantidad_monedas_short,
                    "Precio de take profit": precio_tp}
        elif self.gestion_take_profit == "RATIO BENEFICIO/PERDIDA":
            precio_tp = round(abs(abs(self.entrada_short - self.entrada_stoploss) * self.ratio - self.entrada_short), self.cantidad_decimales_precio)
            return {"Volumen monedas total": self.cantidad_monedas_short,
                    "Precio de take profit": precio_tp}
        else: # "LCD (Carga y Descarga)"
            pass

    # Funcion para calcular el volumen de las monedas
    def vol_monedas(self):
        if self.gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT":
            self.cantidad_monedas_short = round((self.monto_de_sl ) / abs(self.entrada_short - self.entrada_stoploss), self.cantidad_decimales_monedas)
            return {"Precio de entrada" : self.entrada_short,
                    "Volumen monedas total": self.cantidad_monedas_short,
                    "Precio de stop loss": self.entrada_stoploss}



# COMPROBACIÓN DEL MODULO

#""" # Diccionario de ensayo para comprobación sin la función entrada_de_datos
datos_de_entrada = {
            "gestion_seleccionada": "UNIDERECCIONAL SHORT" , # UNIDIRECCIONAL SHORT LONG - DOBLE TAP - SNOW BALL
            "gestion_de_entrada": "LIMITE", # MERCADO - LIMITE - BBO
            "entrada_long": 0.2589,
            "entrada_short": 0.2574,
            "porcentaje_dist_reentradas": 2,
            "cantidad_usdt_long" : 10,
            "cantidad_usdt_short" : 10,
            "cantidad_monedas_long": 39,
            "cantidad_monedas_short": 39,
            "modo_seleccionado": "% DE REENTRADAS", # % DE REENTRADAS - MARTINGALA - AGRESIVO
            "porcentaje_vol_reentrada": 50,
            "monto_de_sl": 10.0,
            "entrada_stoploss": 0.2400,
            "cantidad_de_reentradas": 4,
            "cantidad_decimales_monedas": 0,
            "cantidad_decimales_precio": 4,
            "valor_pips": "0.0001",
            "gestion_take_profit": "RATIO BENEFICIO/PERDIDA", # "% TAKE PROFIT" - "LCD (Carga y Descarga)"
            "ratio": 2
            }
#"""

# Empleando el modulo Entrada_de_datos
#Datos_calculados = PosicionLong(entrada_de_datos())
#Datos_calculados = PosicionShort(entrada_de_datos())

# Empleando el diccionario de ensayo
Datos_calculados_long= PosicionLong(datos_de_entrada)
Datos_calculados_short= PosicionShort(datos_de_entrada)

# Long
#pprint.pprint(Datos_calculados_long.recompras())
#pprint.pprint(Datos_calculados_long.vol_monedas())
#pprint.pprint(Datos_calculados_long.take_profit())
#pprint.pprint(Datos_calculados_long.stop_loss())
#pprint.pprint(Datos_calculados_long.snow_ball())

# Short
print("\nDATOS DE CLASE LA SHORT:")
pprint.pprint(Datos_calculados_short.recompras())
#pprint.pprint(Datos_calculados_short.vol_monedas())
#pprint.pprint(Datos_calculados_short.take_profit())
#pprint.pprint(Datos_calculados_short.stop_loss())
#pprint.pprint(Datos_calculados_short.snow_ball())

""" 
Para cambiar un dato de los diccionarios resultantes de la clase
debemos cambiar el valor de la variable en el diccionario de entrada y
volver a instanciar (ejecutar) la clase con el nuevo diccionario de entrada.
No es necesario crear una nueva variable para igualarla con algun valor extraido 
de los diccionarios resultantes de la clase.
"""

# nueva_entrada_short = Datos_calculados_short.recompras()["Precios promedios"][-2]
datos_de_entrada["entrada_short"] = Datos_calculados_short.recompras()["Precios promedios"][-1] #nueva_entrada_short
Datos_calculados_short = PosicionShort(datos_de_entrada)

print("\nDatos de Snow ball SHORT:")
pprint.pprint(Datos_calculados_short.snow_ball())