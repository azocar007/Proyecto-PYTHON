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

        # SELECCIÓN DEL TIPO DE GESTION, DOBLE TAP, UNIDERECCIONAL LONG, UNIDERECCIONAL SHORT ó SNOW BALL
        opciones_de_exchanges = {
            "1": "BINANCE",
            "2": "BYBIT",
            "3": "PHEMEX",
            "4": "BING X",
            "5": "OKX",
            "6": "BITGET",
        }
        seleccion_de_exchanges = input(
            "\nSeleccione con un numero del 1 al 6 el exchange para la operación \n1: BINANCE\n2: BYBIT\n3: PHEMEX\n4: BING X\n5: OKX\n6: BITGET\nIngrese numero de selección:\n"
        )
        exchange_seleccionado = opciones_de_exchanges.get(seleccion_de_exchanges, 0)
        while seleccion_de_exchanges not in opciones_de_exchanges:
            seleccion_de_exchanges = input(
                "\nOpción equivocada, por favor seleccione nuevamante:\n1: DOBLE TAP\n2: UNIDIRECCIONAL LONG\n3: UNIDIRECCIONAL SHORT\n4: SNOW BALL\nIngrese selección:\n"
            )
            exchange_seleccionado = opciones_de_exchanges.get(seleccion_de_exchanges, 0)

        # Ingreso de moneda o activo a tradear
        moneda = input("\nPor favor introduzca el nombre del activo para TRADING:\n")
        moneda = moneda.upper() + "USDT"
        # ENVIA A PANTALLA LOS DATOS INGRESADOS
        print(
            f"""\nLOS DATOS INGRESADOS SON LOS SIGUIENTES:\n\n
        Exchange seleccionado: {exchange_seleccionado}
        Activo: {moneda}"""
        )

        # Lista para almacenar los datos calculados
        datos_seleccionados = [moneda, exchange_seleccionado]
        datoscorrectos = input(
            "\n¿Esta conforme con el exchange y la moneda?\n(si/no): "
        ).lower()
        if datoscorrectos == "si":
            return datos_seleccionados


# Función para la entrada de datos
def entrada_de_datos():
    while True:

        print("\nINGRESO DE DATOS PARA LA OPERACIÓN")

        # SELECCIÓN DEL TIPO DE GESTION, DOBLE TAP, UNIDERECCIONAL LONG, UNIDERECCIONAL SHORT ó SNOW BALL
        opciones_de_gestion = {
            "1": "DOBLE TAP",
            "2": "UNIDIRECCIONAL LONG",
            "3": "UNIDIRECCIONAL SHORT",
            "4": "SNOW BALL",
            "5": "2:1 LONG",
            "6": "2:1 SHORT",
        }

        seleccion_de_gestion = input(
            """\nSeleccione con un numero del 1 al 6 el Modo de gestión de la operación\n
        1: DOBLE TAP
        2: UNIDIRECCIONAL LONG
        3: UNIDIRECCIONAL SHORT
        4: SNOW BALL
        5: 2:1 LONG
        6: 2:1 SHORT
        Ingrese numero de selección: """
        )
        gestion_seleccionada = opciones_de_gestion.get(seleccion_de_gestion, 0)
        while seleccion_de_gestion not in opciones_de_gestion:
            seleccion_de_gestion = input(
                """\nOpción equivocada, por favor seleccione nuevamante:\n
        1: DOBLE TAP
        2: UNIDIRECCIONAL LONG
        3: UNIDIRECCIONAL SHORT
        4: SNOW BALL
        5: 2:1 LONG
        6: 2:1 SHORT
        Ingrese selección: """
            )
            gestion_seleccionada = opciones_de_gestion.get(seleccion_de_gestion, 0)

        # VALORES PARA LAS ENTRADAS Y % DISTANCIA DE REENTRADAS
        if (
            gestion_seleccionada == "UNIDIRECCIONAL SHORT"
            or gestion_seleccionada == "2:1 SHORT"
        ):
            entrada_long = "N/A"
            print("\nPrecio de entrada SHORT")
            entrada_short = validar_numero()
        elif (
            gestion_seleccionada == "UNIDIRECCIONAL LONG"
            or gestion_seleccionada == "2:1 LONG"
        ):
            print("\nPrecio de entrada LONG")
            entrada_long = validar_numero()
            entrada_short = "N/A"
        else:
            print("\nPrecio de entrada LONG")
            entrada_long = validar_numero()
            print("\nPrecio de entrada SHORT")
            entrada_short = validar_numero()
        print("\nPorcentaje de distancia de reentradas")
        porcentaje_dist_reentradas = validar_numero()
        ""
        if gestion_seleccionada == "2:1 LONG":
            print("\nPrecio de Stop Loss")
            entrada_stoploss = validar_numero()
            cantidad_de_entradas = "N/A"
            cantidad_monedas_short = "N/A"
            cantidad_usdt_short = "N/A"
        elif gestion_seleccionada == "2:1 SHORT":
            print("\nPrecio de Stop Loss")
            entrada_stoploss = validar_numero()
            cantidad_de_entradas = "N/A"
            cantidad_monedas_long = "N/A"
            cantidad_usdt_long = "N/A"
        else:
                  
            ""
        # VALORES PARA LA GESTION DEL VOLUMEN DE MONEDAS
        print("\nCantidad de USDT ó MONEDAS para entrada inicial")
        cantidad_monedas1 = validar_numero_str()
        opcion_de_volumen = {"1": "USDT", "2": "MONEDAS"}
        seleccion_volumen = input(
            "\nSeleccione identificador de volumen:\n1: USDT\n2: MONEDAS\nIngrese la opción:\n"
        )
        modo_seleccion_volumen = opcion_de_volumen.get(seleccion_volumen, 0)
        while seleccion_volumen not in opcion_de_volumen:
            seleccion_volumen = input(
                "\nOpción equivocada, por favor seleccione el modo nuevamente:\n1: USDT\n2: MONEDAS\nIngrese la opción:\n"
            )
            modo_seleccion_volumen = opcion_de_volumen.get(seleccion_volumen, 0)
        # SELECCION DE TIPO DE GESTION DE VOLUMEN % DE REENTRADAS, MARTINGALA Ó AGRESIVO
        opciones_de_modo_volumen = {
            "1": "% DE REENTRADAS",
            "2": "MARTINGALA",
            "3": "AGRESIVO",
        }
        selección = input(
            "\nSeleccione con un numero del 1 al 3 el Modo de gestión de volumen\n1: % DE REENTRADAS\n2: MARTINGALA\n3: AGRESIVO\nIngrese numero de selección:\n"
        )
        modo_seleccionado = opciones_de_modo_volumen.get(selección, 0)
        while selección not in opciones_de_modo_volumen:
            selección = input(
                "\nOpción equivocada, por favor seleccione el modo nuevamente:\n1: % DE REENTRADAS\n2: MARTINGALA\n3: AGRESIVO\nIngrese numero de selección:\n"
            )
            modo_seleccionado = opciones_de_modo_volumen.get(selección, 0)
        print("\nPorcentaje de volumen para gestión de reentradas")
        porcentaje_vol_reentrada = validar_numero()

        # VALORES PARA LA GESTION DE RIESGO
        # Monto de Stop Loss
        print("\nMonto para Stop Loss o Cobertura")
        monto_de_sl = validar_numero_str()
        # contar decimales de USDT SL
        cant_decimales_sl = contar_decimales(monto_de_sl)
        # convertir el str del monto_de_sl a numero decimal
        monto_de_sl = float(monto_de_sl)
        # cantidad de entradas
        print("\nCantidad de entradas")
        cantidad_de_entradas = validar_numero_entero()

        # CALCULOS INICIALES BASICOS PARA LA ENTRADA DE DATOS #
        # Cantidad de decimales del precio
        cant_decimales_long = contar_decimales(entrada_long)
        cant_decimales_short = contar_decimales(entrada_short)
        list_cant_dec_precio = [cant_decimales_long, cant_decimales_short]
        cantidad_decimales_precio = max(list_cant_dec_precio)

        if entrada_long == "N/A":
            entrada_long = "N/A"
            entrada_short = round(float(entrada_short), cantidad_decimales_precio)
        elif entrada_short == "N/A":
            entrada_long = round(float(entrada_long), cantidad_decimales_precio)
            entrada_short = "N/A"
        else:
            entrada_long = round(float(entrada_long), cantidad_decimales_precio)
            entrada_short = round(float(entrada_short), cantidad_decimales_precio)

        valor_pips = round(
            10 ** (cantidad_decimales_precio * -1), cantidad_decimales_precio
        )

        # SELECCIÓN DE USDT Ó MONEDAS - CALCULO DE CANTIDAD DE DECIMALES DE MONEDA - CANTIDAD DE MONEDAS

        cantidad_decimales_monedas = contar_decimales(cantidad_monedas1)
        cantidad_monedas1 = abs(float(cantidad_monedas1))
        if modo_seleccion_volumen == "USDT":
            if gestion_seleccionada == "UNIDIRECCIONAL SHORT":
                cantidad_monedas_short = round(
                    float(cantidad_monedas1) / entrada_short, cantidad_decimales_monedas
                )
                cantidad_monedas = cantidad_monedas_short
                cantidad_usdt_short = round(cantidad_monedas_short * entrada_short, 2)
                cantidad_usdt_long = "N/A"
                cantidad_monedas_long = "N/A"
            elif gestion_seleccionada == "UNIDIRECCIONAL LONG":
                cantidad_monedas_long = round(
                    float(cantidad_monedas1) / entrada_long, cantidad_decimales_monedas
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
        print(
            f"""\nLOS DATOS INGRESADOS SON LOS SIGUIENTES:\n\n
        Tipo de gestión: {gestion_seleccionada}
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
            "entrada_long": entrada_long,
            "entrada_short": entrada_short,
            "porcentaje_dist_reentradas": porcentaje_dist_reentradas,
            "cantidad_monedas_long": cantidad_monedas_long,
            "cantidad_monedas_short": cantidad_monedas_short,
            "modo_seleccionado": modo_seleccionado,
            "porcentaje_vol_reentrada": porcentaje_vol_reentrada,
            "monto_de_sl": monto_de_sl,
            "cantidad_de_reentradas": cantidad_de_entradas,
            "cantidad_decimales_monedas": cantidad_decimales_monedas,
            "cantidad_decimales_precio": cantidad_decimales_precio,
            "cant_decimales_sl": cant_decimales_sl,
            "valor_pips": valor_pips,
        }
        datoscorrectos = input(
            "\n¿Esta conforme con los datos ingresados?\n(si/no): "
        ).lower()
        if datoscorrectos == "s":
            return datos_calculados


# COMPROBACIÓN DEL MODULO
# exchange_y_moneda = seleccion_de_exchange()
# datos_de_entrada = entrada_de_datos()
# print(f"EL exchange y la moneda seleccionada son:\n{exchange_y_moneda}")
# print(f"Lista de datos ingresados:\n{datos_de_entrada}")
