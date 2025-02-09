### ENTRADA DE DATOS ###

# Funciones para aceptar solo numeros int y float
def validar_numero(mensaje="Ingresa el valor: "):
    while True:
        user_input = input(mensaje)
        try:
            valor = abs(float(user_input))  # Intentamos convertir el input a float
            if (
                valor.is_integer()
            ):  # Si el valor es un número entero, lo convertimos a int
                return int(valor)
            else:
                return valor  # Si tiene decimales, lo dejamos como float
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número.")


# Función para aceptar solo numeros int
def validar_numero_entero(mensaje="Ingresa el valor: "):
    while True:
        user_input = input(mensaje)
        try:
            valor = abs(int(user_input))  # Intentamos convertir el input a int
            return valor  # valor solo int
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número entero.")


# Funcíon para aceptar numeros devolviendo un string
def validar_numero_str(mensaje="Ingresa el valor: "):
    while True:
        user_input = input(mensaje)
        try:
            float(user_input)  # Intentamos convertir el input a float
            return user_input
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número.")


# Función para calcular la cantidad de decimales de una variable
def contar_decimales(numero):
    numero_str = str(numero)
    if "." in numero_str:
        return len(numero_str.split(".")[1])
    else:
        return 0


# Función para seleccionar el exchange y el activo
def seleccion_de_exchange():
    while True:

        print("\nBIENVENIDO AL BOT DE TRADING AZC 1.0")

        # SELECCIÓN DEL EXCHANGE Y ACTIVO
        opciones_de_exchanges = {
            "1": "BINANCE",
            "2": "BYBIT",
            "3": "PHEMEX",
            "4": "BING X",
            "5": "OKX",
            "6": "BITGET",
        }
        seleccion_de_exchanges = input(
            """\nSeleccione con un numero del 1 al 6 el exchange para la operación
            1: BINANCE
            2: BYBIT
            3: PHEMEX
            4: BING X
            5: OKX
            6: BITGET
            Ingrese numero de selección: """
            )
        exchange_seleccionado = opciones_de_exchanges.get(seleccion_de_exchanges, 0)
        while seleccion_de_exchanges not in opciones_de_exchanges:
            seleccion_de_exchanges = input(
                """\nOpción equivocada, por favor seleccione nuevamante
            1: BINANCE
            2: BYBIT
            3: PHEMEX
            4: BING X
            5: OKX
            6: BITGET
            Ingrese numero de selección: """
            )
            exchange_seleccionado = opciones_de_exchanges.get(seleccion_de_exchanges, 0)

        # Ingreso de moneda o activo a tradear
        moneda = input("\nPor favor introduzca el nombre del activo para TRADING:\n")
        moneda = moneda.upper() + "USDT"
        # ENVIA A PANTALLA LOS DATOS INGRESADOS
        print(
            f"""\nLOS DATOS INGRESADOS SON LOS SIGUIENTES:\n
        Exchange seleccionado: {exchange_seleccionado}
        Activo: {moneda}"""
        )

        # Diccionario para almacenar los datos calculados
        datos_seleccionados = {"simbol" : moneda, "exchange": exchange_seleccionado}
        datoscorrectos = input(
            "\n¿Esta conforme con el exchange y la moneda?\n(si/no): ").lower()
        
        if datoscorrectos == "s" or datoscorrectos == "si":
            return datos_seleccionados


# Función para la entrada de datos
def entrada_de_datos():
    while True:

        print("\nINGRESO DE DATOS PARA LA OPERACIÓN")

        # SELECCIÓN DEL TIPO DE GESTION, DOBLE TAP, UNIDERECCIONAL LONG, UNIDERECCIONAL SHORT, SNOW BALL Ó RATIO PERDIDA:BENEFICIO
        opciones_de_gestion = {
            "1": "DOBLE TAP",
            "2": "UNIDIRECCIONAL LONG",
            "3": "UNIDIRECCIONAL SHORT",
            "4": "SNOW BALL",
            "5": "RATIO BENEFICIO/PERDIDA LONG",
            "6": "RATIO BENEFICIO/PERDIDA SHORT",
        }

        seleccion_de_gestion = input(
            """\nSeleccione con un numero del 1 al 6 el Modo de gestión de la operación
            1: DOBLE TAP
            2: UNIDIRECCIONAL LONG
            3: UNIDIRECCIONAL SHORT
            4: SNOW BALL
            5: RATIO BENEFICIO/PERDIDA LONG
            6: RATIO BENEFICIO/PERDIDA SHORT
            Ingrese numero de selección: """
        )
        gestion_seleccionada = opciones_de_gestion.get(seleccion_de_gestion, 0)
        while seleccion_de_gestion not in opciones_de_gestion:
            seleccion_de_gestion = input(
                """\nOpción equivocada, por favor seleccione nuevamante:
            1: DOBLE TAP
            2: UNIDIRECCIONAL LONG
            3: UNIDIRECCIONAL SHORT
            4: SNOW BALL
            5: RATIO BENEFICIO/PERDIDA LONG
            6: RATIO BENEFICIO/PERDIDA SHORT
            Ingrese numero de selección: """
            )
            gestion_seleccionada = opciones_de_gestion.get(seleccion_de_gestion, 0)

        # SELECCIÓN DE TIPO DE ENTRADA
        opciones_de_entrada = {
            "1": "MERCADO",
            "2": "BBO",
            "3": "LIMITE"
        }
        seleccion_de_entrada = input(
            """\nSeleccione con un numero del 1 al 3 el Modo de gestión de la operación
            1: MERCADO
            2: BBO
            3: LIMITE
            Ingrese numero de selección: """
        )
        gestion_de_entrada = opciones_de_entrada.get(seleccion_de_entrada, 0)
        while seleccion_de_entrada not in opciones_de_entrada:
            seleccion_de_entrada = input(
                """\nOpción equivocada, por favor seleccione nuevamante:
            1: MERCADO
            2: BBO
            3: LIMITE
            Ingrese numero de selección: """
            )
            gestion_de_entrada = opciones_de_entrada.get(seleccion_de_entrada, 0)

        # VALORES PARA LAS ENTRADAS
        if gestion_de_entrada == "MERCADO":
            entrada_long = "MARKET"
            entrada_short = "MARKET"
            valor_pips = "N/A"
        elif gestion_de_entrada == "BBO":
            entrada_long = "BBO"
            entrada_short = "BBO"
            valor_pips = "N/A"
        else: # gestion_de_entrada == "LIMITE":
            if (
                gestion_seleccionada == "UNIDIRECCIONAL SHORT"
                or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT"
            ):
                entrada_long = "N/A"
                print("\nPrecio de entrada SHORT")
                entrada_short = validar_numero()
            elif (
                gestion_seleccionada == "UNIDIRECCIONAL LONG"
                or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG"
            ):
                print("\nPrecio de entrada LONG")
                entrada_long = validar_numero()
                entrada_short = "N/A"
            else:
                print("\nPrecio de entrada LONG")
                entrada_long = validar_numero()
                print("\nPrecio de entrada SHORT")
                entrada_short = validar_numero()

        # VALORES PARA LA GESTION DE REENTRADAS RATIO BENEFICIO/PERDIDA LONG y SHORT
        if gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG":
            print("\nPrecio de Stop Loss, debe ser menor al precio de entrada LONG")
            entrada_stoploss = validar_numero()
            # Validar que el precio de stop loss sea menor al precio de entrada
            while entrada_stoploss >= entrada_long:
                print("\nValor incorrecto, el precio de Stop Loss debe ser menor al precio de entrada LONG")
                entrada_stoploss = validar_numero()

        elif gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT":
            print("\nPrecio de Stop Loss, debe ser mayor al precio de entrada SHORT")
            entrada_stoploss = validar_numero()
            # Validar que el precio de stop loss sea mayor al precio de entrada
            while entrada_stoploss <= entrada_short:
                print("\nValor incorrecto, el precio de Stop Loss debe ser mayor al precio de entrada SHORT")
                entrada_stoploss = validar_numero()

        else: # VALORES PARA LA GESTION DEL VOLUMEN DE MONEDAS y % DISTANCIA DE REENTRADAS
            print("\nPorcentaje de distancia de reentradas")
            porcentaje_dist_reentradas = validar_numero()

            print("\nCantidad de USDT ó MONEDAS para entrada inicial")
            cantidad_monedas1 = validar_numero_str()
            cantidad_decimales_monedas = contar_decimales(cantidad_monedas1)
            cantidad_monedas1 = abs(float(cantidad_monedas1))

            opcion_de_volumen = {
                "1": "USDT",
                "2": "MONEDAS"}
            seleccion_volumen = input(
            """\nSeleccione identificador de volumen:
            1: USDT
            2: MONEDAS
            Ingrese la opción: """
            )
            modo_seleccion_volumen = opcion_de_volumen.get(seleccion_volumen, 0)
            while seleccion_volumen not in opcion_de_volumen:
                seleccion_volumen = input(
            """Opción equivocada, por favor seleccione el modo nuevamente:
            1: USDT
            2: MONEDAS
            Ingrese la opción: """
                )
                modo_seleccion_volumen = opcion_de_volumen.get(seleccion_volumen, 0)
            # Selección de modo de gestión de volumen (% DE REENTRADAS, MARTINGALA, AGRESIVO)
            opciones_de_modo_volumen = {
                "1": "% DE REENTRADAS",
                "2": "MARTINGALA",
                "3": "AGRESIVO"
            }
            selección = input(
            """\nSeleccione con un numero del 1 al 3 el Modo de gestión de volumen:
            1: % DE REENTRADAS
            2: MARTINGALA
            3: AGRESIVO
            Ingrese numero de selección: """
            )
            modo_seleccionado = opciones_de_modo_volumen.get(selección, 0)
            while selección not in opciones_de_modo_volumen:
                selección = input(
            """\nOpción equivocada, por favor seleccione el modo nuevamente:
            1: % DE REENTRADAS
            2: MARTINGALA
            3: AGRESIVO
            Ingrese numero de selección: """
                )
                modo_seleccionado = opciones_de_modo_volumen.get(selección, 0)
            # Porcentaje de volumen para gestión de reentradas
            print("\nPorcentaje de volumen para gestión de reentradas")
            porcentaje_vol_reentrada = validar_numero()
            # Cantidad de entradas
            print("\nCantidad de entradas")
            cantidad_de_entradas = validar_numero_entero()
            entrada_stoploss = "N/A"

        # VALORES PARA LA GESTION DE RIESGO
        # Monto de Stop Loss
        print("\nMonto para Stop Loss o Cobertura")
        monto_de_sl = validar_numero_str()
        cant_decimales_sl = contar_decimales(monto_de_sl)
        monto_de_sl = float(monto_de_sl)

        # CALCULOS INICIALES BASICOS PARA LA ENTRADA DE DATOS #
        # Cantidad de decimales del precio
        cant_decimales_long = contar_decimales(entrada_long)
        cant_decimales_short = contar_decimales(entrada_short)
        cant_decimales_sl = contar_decimales(entrada_stoploss)
        list_cant_dec_precio = [cant_decimales_long, cant_decimales_short, cant_decimales_sl]
        cantidad_decimales_precio = max(list_cant_dec_precio)

        if entrada_long == "N/A":
            entrada_short = round(float(entrada_short), cantidad_decimales_precio)
        elif entrada_short == "N/A":
            entrada_long = round(float(entrada_long), cantidad_decimales_precio)
        else:
            entrada_long = round(float(entrada_long), cantidad_decimales_precio)
            entrada_short = round(float(entrada_short), cantidad_decimales_precio)
        # Valor de un pip
        valor_pips = round(10 ** (cantidad_decimales_precio * -1), cantidad_decimales_precio)

        # SELECCIÓN DE USDT Ó MONEDAS - CALCULO DE CANTIDAD DE DECIMALES DE MONEDA - CANTIDAD DE MONEDAS
        if (gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG" or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT"):
            modo_seleccion_volumen = "USDT"
            entrada_stoploss = round(float(entrada_stoploss), cantidad_decimales_precio)
            cantidad_decimales_monedas = cant_decimales_sl
            # Variables que no aplican en la gestion ratio beneficio/perdida
            cantidad_de_entradas = "N/A"
            cantidad_monedas_short = "N/A"
            cantidad_usdt_short = "N/A"
            cantidad_de_entradas = "N/A"
            porcentaje_dist_reentradas = "N/A"
            modo_seleccionado="N/A"
            porcentaje_vol_reentrada = "N/A"

        if modo_seleccion_volumen == "USDT":
            if (gestion_seleccionada == "UNIDIRECCIONAL SHORT" or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT"):
                cantidad_monedas_short = round(
                    float(monto_de_sl) / entrada_short, cant_decimales_sl
                )
                cantidad_monedas = cantidad_monedas_short
                cantidad_usdt_short = round(cantidad_monedas_short * entrada_short, 2)
                cantidad_usdt_long = "N/A"
                cantidad_monedas_long = "N/A"
            elif (gestion_seleccionada == "UNIDIRECCIONAL LONG" or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG"):
                cantidad_monedas_long = round(
                    float(monto_de_sl) / entrada_long, cant_decimales_sl
                )
                cantidad_monedas = cantidad_monedas_long
                cantidad_usdt_long = round(cantidad_monedas_long * entrada_long, 2)
                cantidad_usdt_short = "N/A"
                cantidad_monedas_short = "N/A"
            else:
                cantidad_monedas_long = round(
                    float(cantidad_monedas1) / entrada_long, cantidad_decimales_monedas
                )
                cantidad_monedas = cantidad_monedas_short = cantidad_monedas_long
                cantidad_usdt_long = round(cantidad_monedas_long * entrada_long, 2)
                cantidad_usdt_short = round(cantidad_monedas_short * entrada_short, 2)
        else:  # modo_seleccion_volumen == "MONEDAS":
            cantidad_monedas = cantidad_monedas_long = cantidad_monedas_short = (
                cantidad_monedas1
            )
            if gestion_seleccionada == "UNIDIRECCIONAL SHORT":
                cantidad_usdt_short = round(float(cantidad_monedas) * entrada_short, 2)
                cantidad_monedas_long = "N/A"
                cantidad_usdt_long = "N/A"
            elif gestion_seleccionada == "UNIDIRECCIONAL LONG":
                cantidad_usdt_long = round(float(cantidad_monedas) * entrada_long, 2)
                cantidad_monedas_short = "N/A"
                cantidad_usdt_short = "N/A"
            else:
                cantidad_usdt_long = round(float(cantidad_monedas) * entrada_long, 2)
                cantidad_usdt_short = round(float(cantidad_monedas) * entrada_short, 2)

        # ENVIA A PANTALLA LOS DATOS INGRESADOS
        if (gestion_seleccionada == "RATIO BENEFICIO/PERDIDA LONG" or gestion_seleccionada == "RATIO BENEFICIO/PERDIDA SHORT"):
            # Gestion RATIO BENEFICIO/PERDIDA LONG y SHORT
            print(
                f"""\nLOS DATOS INGRESADOS SON LOS SIGUIENTES:\n\n
            Tipo de gestión: {gestion_seleccionada}
            Tipo de entrada: {gestion_de_entrada}
            
            Precio de entrada LONG: {entrada_long}
            Precio de entrada SHORT: {entrada_short}
            
            Volumen de entrada inicial:
            LONG: {cantidad_monedas_long} MONEDAS => {cantidad_usdt_long} USDT
            SHORT: {cantidad_monedas_short} MONEDAS => {cantidad_usdt_short} USDT
            
            Monto de STOP LOSS ó COBERTURA: {monto_de_sl} USDT
            Precion de Stop Loss: {entrada_stoploss}\n"""
            )
        else: # Gestion con recompras
            print(
                f"""\nLOS DATOS INGRESADOS SON LOS SIGUIENTES:\n\n
            Tipo de gestión: {gestion_seleccionada}
            Tipo de entrada: {gestion_de_entrada}
            
            Precio de entrada LONG: {entrada_long}
            Precio de entrada SHORT: {entrada_short}
            Porcentaje de distancia de reentradas: {porcentaje_dist_reentradas}%\n
            
            Volumen de entrada inicial:
            LONG: {cantidad_monedas_long} MONEDAS => {cantidad_usdt_long} USDT
            SHORT: {cantidad_monedas_short} MONEDAS => {cantidad_usdt_short} USDT
            
            Modo gestión de volumen: {modo_seleccionado}
            Porcentaje de volumen para gestión de reentradas: {porcentaje_vol_reentrada}%\n
            Monto de STOP LOSS ó COBERTURA: {monto_de_sl} USDT
            Cantidad de entradas: {cantidad_de_entradas}\n"""
            )

        # Dicionario para almacenar los datos calculados
        datos_calculados = {
            "gestion_seleccionada": gestion_seleccionada,
            "gestion_de_entrada": gestion_de_entrada,
            "entrada_long": entrada_long,
            "entrada_short": entrada_short,
            "porcentaje_dist_reentradas": porcentaje_dist_reentradas,
            "cantidad_monedas_long": cantidad_monedas_long,
            "cantidad_monedas_short": cantidad_monedas_short,
            "modo_seleccionado": modo_seleccionado,
            "porcentaje_vol_reentrada": porcentaje_vol_reentrada,
            "monto_de_sl": monto_de_sl,
            "entrada_stoploss": entrada_stoploss,
            "cantidad_de_reentradas": cantidad_de_entradas,
            "cantidad_decimales_monedas": cantidad_decimales_monedas,
            "cantidad_decimales_precio": cantidad_decimales_precio,
            "cant_decimales_sl": cant_decimales_sl,
            "valor_pips": valor_pips}

        datoscorrectos = input("\n¿Esta conforme con los datos ingresados?\n(si/no): ").lower()
        if datoscorrectos == "s"or datoscorrectos == "si":
            return datos_calculados


# COMPROBACIÓN DEL MODULO
#exchange_y_moneda = seleccion_de_exchange()
datos_de_entrada = entrada_de_datos()
# print(f"EL exchange y la moneda seleccionada son:\n{exchange_y_moneda}")
# print(f"Lista de datos ingresados:\n{datos_de_entrada}")
# git push origin main --force comando en la terminal para forzar la subida al repositorio
