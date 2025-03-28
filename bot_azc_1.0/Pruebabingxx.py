import time
import threading

class BingX:
    def __init__(self, trade_type: str = "contractPerpetual"):
        self.ws_url = "wss://open-api-swap.bingx.com/swap-market"
        self.last_price = None
        self.ws = None  # Guarda la instancia del WebSocket
    
    def start_websocket(self, symbol: str = "DOGE-USDT", interval: str = "1m"):
        import websocket
        import json
        import gzip
        import io
        
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
                    self.last_price = float(data["data"][0]["c"])  # Guardar último precio
                    print(f"💰 Precio actualizado: {self.last_price}")

            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")

        def on_error(ws, error):
            print(f"⚠️ Error en WebSocket: {error}")
            self.reconnect(symbol, interval)  # Intentar reconectar

        def on_close(ws, close_status_code, close_msg):
            print("🔴 Conexión WebSocket cerrada. Intentando reconectar...")
            self.reconnect(symbol, interval)  # Intentar reconectar
        
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


# Crear instancia de BingX
bingx = BingX()

# Iniciar el WebSocket en un hilo separado
threading.Thread(target=bingx.start_websocket, args=("DOGE-USDT", "1m")).start()

# Bucle para monitorear el último precio sin bloquear el WebSocket
while True:
    time.sleep(5)
    if bingx.last_price is not None:
        print(f"🔄 Último precio disponible: {bingx.last_price}")
    else:
        print("⏳ Esperando datos de precio...")
