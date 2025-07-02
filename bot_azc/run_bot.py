""" Archivo para correr el bot de trading AZC con la estrategia definida. """

from exchanges.BingX import BingX
from strategys.estrategias_azc import SMA_MACD_BB, SMA_BB
from exchanges import Modos_de_gestion_operativa as mgo


""" Datos de configuración del bot de trading. """

# Estos datos son utilizados por el bot para operar en el exchange.
Datos = {
            "symbol": "sui",
            "positionside": "LONG",
            "modo_gestion": "RATIO BENEFICIO/PERDIDA", # "RECOMPRAS", "RATIO BENEFICIO/PERDIDA", "SNOW BALL"
            "monto_sl": 1.0,
            "type": "LIMIT",
            "precio_entrada": 0,
            "gestion_take_profit": "RATIO BENEFICIO/PERDIDA",
            "ratio": 2,
            "gestion_vol": "MARTINGALA",
            "cant_ree": 6,
            "dist_ree": 2,
            "porcentaje_vol_ree": 0,
            "monedas": 40,
            "usdt": 0,
            "segundos": 10,
            "temporalidad": "5m",
            "cant_velas": 400
            }

# Estrategia a utilizar en el bot de trading.
Estrategia = SMA_BB

# Inicializa el bot de trading con la estrategia y los datos.
Bot = BingX(Estrategia, Datos)
MonitorMemoria = mgo.Monitor_Memoria()

def main():

    """ Función principal para iniciar el bot de trading. """
    try:
        # Inicia monitor de memoria RAM
        MonitorMemoria.iniciar()

        # Inicia el bot de trading
        Bot.monitor_open_positions()

    except Exception as e:
        print("\n❌ Bot detenido por:")
        print(e)

if __name__ == "__main__":
    main()
