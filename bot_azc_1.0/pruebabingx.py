### ENSAYOS DE LA API DE BING X CODIGOS DE LA PAGINA ###
import json
import gzip
import io
import websocket
import requests
import threading
import time


class BingX:
    def __init__(self):
        self.ws_url = "wss://open-api-swap.bingx.com/swap-market"
        self.last_price = None  # Almacenará el último precio recibido

    def get_price_stream(self, symbol: str = "BTC-USDT", interval: str = "1m"):
        channel = {
            "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
            "reqType": "sub",
            "dataType": f"{symbol}@kline_{interval}"
        }

        def on_open(ws):
            print(f"📡 Conectado a WebSocket para {symbol}")
            ws.send(json.dumps(channel))

        def on_message(ws, message):
            try:
                compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
                decompressed_data = compressed_data.read().decode('utf-8')
                data = json.loads(decompressed_data)

                if "data" in data and len(data["data"]) > 0:
                    self.last_price = float(data["data"][0]["c"])
                    print(f"💰 Último precio recibido: {self.last_price}")

                    # Ejecutar estrategia en tiempo real
                    self.check_strategy(self.last_price)
                    """ Aqui ocurre la activacón para aperturas de posiciones """

            except Exception as e:
                print(f"⚠️ Error procesando el mensaje: {e}")

        def on_error(ws, error):
            print(f"⚠️ Error en WebSocket: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("🔴 Conexión WebSocket cerrada!")

        ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()

    def check_strategy(self, last_price):
        """
        Aquí defines la lógica de trading.
        :param last_price: Último precio recibido.
        """
        # Configurar un umbral de compra y venta
        umbral_compra = 0.18800
        umbral_venta = 0.19000

        if last_price <= umbral_compra:
            print("📉 Precio bajo detectado. Oportunidad de COMPRA 💰")
            # Aquí puedes llamar a un método para abrir una orden de compra
        elif last_price >= umbral_venta:
            print("📈 Precio alto detectado. Oportunidad de VENTA 🔥")
            # Aquí puedes llamar a un método para cerrar la operación

    def start_websocket(self, symbol="DOGE-USDT"):
        """
        Ejecuta el WebSocket en un hilo separado para poder seguir ejecutando código.
        """
        thread = threading.Thread(target=self.get_price_stream, args=(symbol,))
        thread.daemon = True  # Se cerrará automáticamente cuando termine el programa
        thread.start()


# 🔥 EJEMPLO DE USO
bingx = BingX()
bingx.start_websocket(symbol="DOGE-USDT")

# Ahora el WebSocket está corriendo en segundo plano y podemos seguir ejecutando código
while True:
    time.sleep(5)  # Simula otras tareas mientras el WebSocket sigue corriendo
    if bingx.last_price is not None:
        print(f"🔄 Último precio disponible: {bingx.last_price}")
        bingx.start_websocket(symbol="DOGE-USDT")
    else:
        print("⏳ Esperando datos de precio...")
