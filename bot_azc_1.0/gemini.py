import json
import websocket
import gzip
import io

class MyTradingClass:

    def __init__(self):
        # ... Tu inicialización existente ...
        self.url = "wss://open-api-swap.bingx.com/swap-market"
        self.ws = None
        # ... Otras inicializaciones ...

    def start_bingx_websocket(self, symbol: str = "BTC-USDT", data_type: str = "1m"):
        """Inicia la conexión WebSocket de BingX para un símbolo específico."""
        channel_data = {
            "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",  # Reemplaza con tu ID único
            "reqType": "sub",
            "dataType": f"{symbol}@kline_{data_type}"
        }
        self.channel_data = channel_data

        def on_open(ws):
            print('WebSocket BingX connected')
            sub_str = json.dumps(self.channel_data)
            ws.send(sub_str)
            print("Subscribed to :", sub_str)

        def on_message(ws, message):
            compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
            utf8_data = compressed_data.read().decode('utf-8')
            data = json.loads(utf8_data)
            print("Datos del activo:", data["dataType"], data["data"]) #"Precio actual:", data["data"][0]["c"])  # Mensaje recibido
            if utf8_data == "Ping":
                ws.send("Pong")

        def on_error(ws, error):
            print("BingX WebSocket Error:", error)

        def on_close(ws, close_status_code, close_msg):
            print('BingX WebSocket connection closed!')

        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.ws.run_forever()

    # ... Otros métodos de tu clase ...

# Ejemplo de uso:
if __name__ == "__main__":
    my_trading_instance = MyTradingClass()
    symbol = "DOGE-USDT"
    temporalidad = "1h"
    # Para seguir ETH-USDT con velas de 1 minuto:
    #my_trading_instance.start_bingx_websocket("DOGE-USDT", "1h")
    my_trading_instance.start_bingx_websocket(symbol, temporalidad)
    # Para seguir XRP-USDT con datos de ticker:
    #my_trading_instance.start_bingx_websocket("DOGE-USDT", "ticker")

#ARROJA EL DATO DEL PRECIO CON LOS DEMAS PARAMETROS Y ADMITE LA MODIFICACIÓN DEL ACTIVO COMO PARAMETRO AL LLAMAR EL METODO DE LA CLASE