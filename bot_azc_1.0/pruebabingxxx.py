import time
import threading
import json
import gzip
import io
import websocket


class BingX:
    def __init__(self):
        self.ws_url = "wss://open-api-swap.bingx.com/swap-market"
        self.last_price = None
        self.ws = None
        self.ws_running = False  # Controla si el WebSocket está activo
        self.umbral_compra = 0.18800
        self.umbral_venta = 0.19000


    def start_websocket(self, symbol: str = "BTC-USDT", interval: str = "1m"):
        """Inicia una conexión WebSocket evitando múltiples conexiones simultáneas"""
        if self.ws_running:
            print("⚠️ WebSocket ya está en ejecución, evitando conexión duplicada.")
            return

        self.ws_running = True  # Marcar WebSocket como activo

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

                if "data" in data:
                    self.last_price = float(data["data"][0]["c"])
                    print(f"Inf. vela: {data["dataType"]}: {data["data"]}")
                    #print(f"💰 Precio actualizado: {self.last_price}")
                    self.check_strategy(self.last_price) # Ejecutar estrategia en tiempo real
                    """ Aqui ocurre la activacón para aperturas de posiciones """


            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")

        def on_error(ws, error):
            print(f"⚠️ Error en WebSocket: {error}")
            self.ws_running = False  # Marcar WebSocket como inactivo
            self.reconnect(symbol, interval)

        def on_close(ws, close_status_code, close_msg):
            print("🔴 Conexión WebSocket cerrada. Intentando reconectar...")
            self.ws_running = False  # Marcar WebSocket como inactivo
            self.reconnect(symbol, interval)

        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.ws.run_forever()

    def reconnect(self, symbol, interval):
        """ Intenta reconectar el WebSocket después de 5 segundos """
        time.sleep(5)
        print("♻️ Reintentando conexión...")
        threading.Thread(target=self.start_websocket, args=(symbol, interval)).start()

    def check_strategy(self, last_price):
        """
        Aquí defines la lógica de trading.
        :param last_price: Último precio recibido.
        """
        # Configurar un umbral de compra y venta
        if last_price <= self.umbral_compra:
            print("📉 Precio bajo detectado. Oportunidad de COMPRA 💰")
            # Aquí puedes llamar a un método para abrir una orden de compra
        elif last_price >= self.umbral_venta:
            print("📈 Precio alto detectado. Oportunidad de VENTA 🔥")
            # Aquí puedes llamar a un método para cerrar la operación



# 🔥 INICIAR EL WEBSOCKET 🔥
if __name__ == "__main__":
    bingx = BingX()
    threading.Thread(target=bingx.start_websocket, args=("DOGE-USDT", "1m")).start()

    # Bucle principal para monitorear el último precio sin abrir múltiples conexiones
    while True:
        time.sleep(5)
        if bingx.last_price is not None:
            print(f"🔄 Último precio disponible: {bingx.last_price}")
        else:
            print("⏳ Esperando datos de precio...")
