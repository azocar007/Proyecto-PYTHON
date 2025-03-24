### ENSAYOS DE LA API DE BING X CODIGOS DE LA PAGINA ###
import pprint
import websocket
import json
import threading
import time
import gzip
import io


URL="wss://open-api-swap.bingx.com/swap-market"
symbol = "BTC-USDT"
CHANNEL= {
    "id":"e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
    "reqType": "sub",
    "dataType": "DOGE-USDT@kline_1m"}
class Test(object):

    def __init__(self):
        self.url = URL 
        self.ws = None

    def on_open(self, ws):
        print('WebSocket connected')
        subStr = json.dumps(CHANNEL)
        ws.send(subStr)
        print("Subscribed to :",subStr)

    def on_data(self, ws, string, type, continue_flag):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(string), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        print(utf8_data)

    def on_message(self, ws, message):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        print(utf8_data)  #this is the message you need 
        if utf8_data == "Ping": # this is very important , if you receive 'Ping' you need to send 'Pong' 
           ws.send("Pong")

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            # on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()


if __name__ == "__main__":
    test = Test()
    test.start()

"""
class BingXWebSocket:
    def __init__(self):
        self.ws_connections = {}
        self.price_data = {}
        
    def initialize_websocket(self, symbol):
        symbol = symbol.upper()
        
        if symbol in self.ws_connections:
            print(f"Ya existe una conexión WebSocket para {symbol}")
            return
            
        def on_message(ws, message):
            try:
                # Intentar descomprimir el mensaje
                with io.BytesIO(message) as buf:
                    with gzip.GzipFile(fileobj=buf, mode='rb') as f:
                        decompressed_msg = f.read().decode('utf-8')
                data = json.loads(decompressed_msg)
                
                if 'data' in data and 'lastPrice' in data['data']:
                    self.price_data[symbol] = float(data['data']['lastPrice'])
                    print(f"\r[{symbol}] Precio: {self.price_data[symbol]}", end="", flush=True)
                    
            except gzip.BadGzipFile:
                try:
                    data = json.loads(message.decode('utf-8'))
                    if 'data' in data and 'lastPrice' in data['data']:
                        self.price_data[symbol] = float(data['data']['lastPrice'])
                except Exception as e:
                    print(f"Error procesando mensaje no comprimido: {e}")
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
                
        def on_error(ws, error):
            print(f"\nError en WebSocket {symbol}: {error}")
            
        def on_close(ws, close_status_code, close_msg):
            print(f"\nConexión cerrada para {symbol}")
            if symbol in self.ws_connections:
                del self.ws_connections[symbol]
                
        def on_open(ws):
            print(f"\nConexión WebSocket establecida para {symbol}")
            subscribe_msg = {
                "id": "1",
                "reqType": "sub",
                "dataType": f"{symbol}@trade"
            }
            ws.send(json.dumps(subscribe_msg))
            
        ws_url = "wss://open-api-swap.bingx.com/swap-market" #"wss://open-api-ws.bingx.com/market"
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        self.ws_connections[symbol] = {
            'ws': ws,
            'thread': None,
            'running': True
        }
        
        def run_websocket():
            while self.ws_connections.get(symbol, {}).get('running', False):
                try:
                    ws.run_forever(
                        ping_interval=20,
                        ping_timeout=10,
                        origin="https://www.bingx.com"
                    )
                except Exception as e:
                    print(f"Error en run_forever: {e}")
                time.sleep(5)
                
        thread = threading.Thread(target=run_websocket)
        thread.daemon = True
        self.ws_connections[symbol]['thread'] = thread
        thread.start()
        
    def get_realtime_price(self, symbol):
        symbol = symbol.upper()
        if symbol not in self.ws_connections:
            self.initialize_websocket(symbol)
            time.sleep(1)
        return self.price_data.get(symbol)
        
    def close_websocket(self, symbol):
        symbol = symbol.upper()
        if symbol in self.ws_connections:
            self.ws_connections[symbol]['running'] = False
            self.ws_connections[symbol]['ws'].close()
            if self.ws_connections[symbol]['thread']:
                self.ws_connections[symbol]['thread'].join(timeout=5)
            del self.ws_connections[symbol]
            if symbol in self.price_data:
                del self.price_data[symbol]
                
    def close_all_websockets(self):
        for symbol in list(self.ws_connections.keys()):
            self.close_websocket(symbol)

# Ejecución del programa
if __name__ == "__main__":
    print("Iniciando monitor de precios de BingX...")
    
    # 1. Crear instancia del WebSocket
    bingx_ws = BingXWebSocket()
    
    # 2. Configurar los pares a monitorear
    symbols = ["DOGE-USDT"]  # Puedes añadir más pares
    
    # 3. Iniciar las conexiones WebSocket
    for symbol in symbols:
        bingx_ws.initialize_websocket(symbol)
    
    try:
        # 4. Bucle principal para mostrar precios
        print("\nMonitoreando precios (presiona Ctrl+C para detener):")
        while True:
            time.sleep(1)
            # Puedes usar get_realtime_price() en tu lógica de trading
            
    except KeyboardInterrupt:
        # 5. Limpieza al salir
        print("\nDeteniendo monitor de precios...")
        bingx_ws.close_all_websockets()
        print("Conexiones cerradas correctamente.")
        
"""