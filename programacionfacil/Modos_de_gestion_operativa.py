        ### MODOS DE GESTION ###

from Entrada_de_datos import entrada_de_datos

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
def cal_unidereccional_long(datos_calculados):

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
def cal_unidereccional_short(datos_calculados):

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
def cal_snow_ball(datos_calculados):
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

# Calculos de gestion 2:1 Long y Short
def cal_2a1(datos_calculados):
    modo_gest = 
    
    
    pass

# COMPROBACIÓN DEL MODULO
# Diccionario de ensayo para comprobación sin la función entrada_de_datos
"""
datos_calculados = {"gestion_seleccionada" : "SNOW BALL" , # UNIDIRECCIONAL SHORT LONG - DOBLE TAP - SNOW BALL
                    "entrada_long" : 0.2589 , 
                    "entrada_short" : 0.2574 , 
                    "porcentaje_dist_reentradas" : 2 , 
                    "cantidad_monedas_long" : 39 ,
                    "cantidad_monedas_short" : 39 , 
                    "modo_seleccionado" : "% DE REENTRADAS" , # % DE REENTRADAS - MARTINGALA - AGRESIVO
                    "porcentaje_vol_reentrada" : 50 , 
                    "monto_de_sl" : 10 ,
                    "porcentaje_dist_take_profit" : 5 , 
                    "cantidad_de_reentradas" : 5 , 
                    "cantidad_decimales_monedas" : 0 , 
                    "cantidad_decimales_precio" : 4 , 
                    "cant_decimales_sl" : 2 , 
                    "valor_pips" : 0.0001}
#"""
datos_a_calc = entrada_de_datos()

if datos_a_calc["gestion_seleccionada"] == "DOBLE TAP":

    # Gestion SHORT:
    print("\nDATOS DE GESTION DOBLE TAP:\n")
    lista_reentradas_short, lista_vol_mon_short, vol_mon_total_short, lista_prom_short, lista_stoploss_short, mensaje, volum_usdt_total = cal_unidereccional_short(datos_a_calc)
    print(f"""\nDATOS DE GESTION SHORT:\n
        Las reentradas son: {lista_reentradas_short}
        Los volumenes son:{lista_vol_mon_short}
        El volumen acumulado es: {vol_mon_total_short} Monedas => {volum_usdt_total} USDT
        Los ptos promedios son: {lista_prom_short}
        Los precios de Stop Loss son:{lista_stoploss_short}
        {mensaje}\n""")
    # Gestion LONG:
    lista_reentradas_long, lista_vol_mon_long, vol_mon_total_long, lista_prom_long, lista_stoploss_long, mensaje, volum_usdt_total = cal_unidereccional_long(datos_a_calc)
    print(f"""\nDATOS DE GESTION LONG:\n
        Las reentradas son: {lista_reentradas_long}
        Los volumenes son:{lista_vol_mon_long}
        El volumen acumulado es: {vol_mon_total_long} Monedas => {volum_usdt_total} USDT
        Los ptos promedios son: {lista_prom_long}
        Los precios de Stop Loss son:{lista_stoploss_long}
        {mensaje}\n""")

elif datos_a_calc["gestion_seleccionada"] == "UNIDIRECCIONAL LONG":
    #pass
    lista_reentradas_long, lista_vol_mon_long, vol_mon_total_long, lista_prom_long, lista_stoploss_long, mensaje, volum_usdt_total = cal_unidereccional_long(datos_a_calc)
    print(f"""\nDATOS DE GESTION UNIDIRECCIONAL LONG:
        Las reentradas son: {lista_reentradas_long}
        Los volumenes son:{lista_vol_mon_long}
        El volumen acumulado es: {vol_mon_total_long} Monedas => {volum_usdt_total} USDT
        Los ptos promedios son: {lista_prom_long}
        Los precios de Stop Loss son:{lista_stoploss_long}
        {mensaje}\n""")

elif datos_a_calc["gestion_seleccionada"] == "UNIDIRECCIONAL SHORT":
    #pass
    lista_reentradas_short, lista_vol_mon_short, vol_mon_total_short, lista_prom_short, lista_stoploss_short, mensaje, volum_usdt_total = cal_unidereccional_short(datos_a_calc)
    print(f"""\nDATOS DE GESTION UNIDIRECCIONAL SHORT:
        Las reentradas son: {lista_reentradas_short}
        Los volumenes son:{lista_vol_mon_short}
        El volumen acumulado es: {vol_mon_total_short} Monedas => {volum_usdt_total} USDT
        Los ptos promedios son: {lista_prom_short}
        Los precios de Stop Loss son:{lista_stoploss_short}
        {mensaje}\n""")

else: # modo_gestion == "SNOW BALL"
    #pass
    lista_reentradas_long, lista_reentradas_short, lista_vol_monendas, vol_mon_total, lista_prom_long, lista_prom_short, lista_stoploss_long, lista_stoploss_short = cal_snow_ball(datos_a_calc)
    print(f"\nDATOS DE GESTION SNOW BALL:\n\nReentradas LONG: {lista_reentradas_long}\nPuntos promedios LONG: {lista_prom_long}\nPuntos de Stop Loss LONG: {lista_stoploss_long}\n\nLos volumenes de monedas son: {lista_vol_monendas},\nVolumen total acumulado: {vol_mon_total}\n\nPuntos de Stop Loss SHORT: {lista_stoploss_short}\nPuntos promedios SHORT: {lista_prom_short}\nReentradas SHORT: {lista_reentradas_short}\n")