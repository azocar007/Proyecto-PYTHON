import json
import websocket
import gzip
import io
import threading

class BingXExchange:
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_connections = {}
        self.price_data = {}
        self.kline_data = {}  # Para almacenar datos de velas
        
    def start_kline_websocket(self, symbol, interval='1m'):
        """
        Inicia WebSocket para datos de velas (kline)
        :param symbol: Par de trading (ej: 'BTC-USDT')
        :param interval: Intervalo de tiempo (1m, 5m, 15m, etc.)
        """
        symbol = symbol.upper()
        if symbol in self.ws_connections:
            print(f"Ya existe una conexión WebSocket para {symbol}")
            return

        ws_url = "wss://open-api-swap.bingx.com/swap-market"
        
        def on_open(ws):
            print(f'WebSocket conectado para {symbol}@{interval}')
            channel = {
                "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",  # Puedes generar un UUID único
                "reqType": "sub",
                "dataType": f"{symbol}@kline_{interval}"
            }
            ws.send(json.dumps(channel))
            print(f"Suscrito a: {symbol}@kline_{interval}")

        def on_message(ws, message):
            try:
                # Descompresión del mensaje
                with gzip.GzipFile(fileobj=io.BytesIO(message)) as f:
                    decompressed = f.read().decode('utf-8')
                
                if decompressed == "Ping":
                    ws.send("Pong")
                    return
                
                data = json.loads(decompressed)
                print("Datos recibidos:", data)  # Para depuración
                
                # Procesamiento de datos de vela
                if 'data' in data and 'k' in data['data']:
                    kline = data['data']['k']
                    self.kline_data[symbol] = {
                        'timestamp': kline['t'],
                        'open': float(kline['o']),
                        'high': float(kline['h']),
                        'low': float(kline['l']),
                        'close': float(kline['c']),
                        'volume': float(kline['v'])
                    }
                    print(f"Vela actualizada {symbol}: {self.kline_data[symbol]}")

            except Exception as e:
                print(f"Error procesando mensaje: {e}")

        def on_error(ws, error):
            print(f"Error en WebSocket {symbol}: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f'Conexión cerrada para {symbol}')
            if symbol in self.ws_connections:
                del self.ws_connections[symbol]

        # Configurar WebSocket
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Guardar conexión y ejecutar en hilo separado
        self.ws_connections[symbol] = {
            'ws': ws,
            'thread': None,
            'running': True
        }

        def run_websocket():
            while self.ws_connections.get(symbol, {}).get('running', False):
                try:
                    ws.run_forever(ping_interval=20, ping_timeout=10)
                except Exception as e:
                    print(f"Error en run_forever: {e}")
                time.sleep(5)

        thread = threading.Thread(target=run_websocket)
        thread.daemon = True
        self.ws_connections[symbol]['thread'] = thread
        thread.start()

    def get_latest_kline(self, symbol):
        """
        Obtiene los últimos datos de vela para un símbolo
        :param symbol: Par de trading
        :return: Diccionario con datos de vela o None si no disponible
        """
        return self.kline_data.get(symbol.upper())

    def stop_kline_websocket(self, symbol):
        """
        Detiene el WebSocket para un símbolo
        :param symbol: Par de trading
        """
        symbol = symbol.upper()
        if symbol in self.ws_connections:
            self.ws_connections[symbol]['running'] = False
            self.ws_connections[symbol]['ws'].close()
            if self.ws_connections[symbol]['thread']:
                self.ws_connections[symbol]['thread'].join(timeout=5)
            del self.ws_connections[symbol]
            if symbol in self.kline_data:
                del self.kline_data[symbol]
                

if __name__ == "__main__":
    #ensayo
    exchange = BingXExchange()
    exchange.start_kline_websocket("BTC-USDT", "1m")  # Para velas de 1 minuto

    
while True:
    kline_data = exchange.get_latest_kline("BTC-USDT")
    if kline_data:
        print(f"Precio de cierre: {kline_data['close']}")
    time.sleep(1)
    

#NI SIQUIERA INICIA