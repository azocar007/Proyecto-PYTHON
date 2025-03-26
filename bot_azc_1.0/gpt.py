import json
import websocket
import gzip
import io
import requests
import time
import hmac
import hashlib

# Definiendo la clase BingX
class BingX:

    # Inicializa la API con las credenciales y el tipo de trading.
    def __init__(self, trade_type: str = "contractPerpetual"):
        self.api_key = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
        self.api_secret = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
        self.base_url = "https://open-api.bingx.com"
        self.ws_url = "wss://open-api-swap.bingx.com/swap-market"
        self.trade_type = trade_type
        self.session = requests.Session()
        self.session.headers.update({
            "X-BX-APIKEY": self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    """ METODOS PARA OBTENER INFORMACION DE LA CUENTA Y DE LAS MONEDAS """

    # Metodo para generar la firma HMAC SHA256 requerida por la API.
    def _get_signature(self, params: str) -> str:
        return hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()

    # Metodo para obtener el timestamp actual
    def _get_timestamp(self) -> str:
        return str(int(time.time() * 1000))

    # Metodo para obtener la informacion de las velas
    def get_last_candles(self, symbol: str, interval: str = "1m", limit: int = 2):
        url = f"{self.base_url}/openApi/swap/v3/quote/klines?symbol={symbol}&interval={interval}&limit={limit}"
        response = self.session.get(url)
        
        if response.status_code != 200:
            print("ERROR - Código de estado:", response.status_code)
            return []
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("ERROR - No se pudo decodificar la respuesta JSON.")
            return []
        
        candles = data.get("data", [])
        if not isinstance(candles, list) or len(candles) < limit:
            print("ERROR - No se encontraron suficientes datos de velas.")
            return []
        
        return candles

    # Metodo para obtener el precio en tiempo real via WebSocket
    def get_price_stream(self, symbol: str = "BTC-USDT", interval: str = "1m"):
        # Método para conectarse al WebSocket de BingX y recibir el precio en tiempo real
        # Valores validos para los intervalos: 1m - 3m - 5m - 15m - 30m - 1h - 2h - 4h - 6h - 8h - 12h - 1d - 3d - 1w - 1M

        # Definir los datos de suscripción
        channel = {
            "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40", # "price-stream"
            "reqType": "sub",
            "dataType": f"{symbol}@kline_{interval}"
        }

        def on_open(ws):
            """ Se ejecuta cuando se abre la conexión WebSocket """
            print(f"📡 Conectado a WebSocket para {symbol}")
            ws.send(json.dumps(channel))
            print("✅ Suscrito a:", json.dumps(channel))

        def on_message(ws, message):
            """ Se ejecuta cuando se recibe un mensaje desde el WebSocket """
            try:
                # Descomprimir el mensaje si está en formato GZIP
                compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
                decompressed_data = compressed_data.read().decode('utf-8')

                # Convertir el mensaje en JSON
                data = json.loads(decompressed_data)
                print("💰 Precio recibido:", data["dataType"], data["data"])

                # Responder con 'Pong' si el servidor envía 'Ping'
                if decompressed_data == "Ping":
                    ws.send("Pong")
            except Exception as e:
                print(f"❌ Error procesando el mensaje: {e}")

        def on_error(ws, error):
            """ Manejo de errores en la conexión WebSocket """
            print(f"⚠️ Error en WebSocket: {error}")

        def on_close(ws, close_status_code, close_msg):
            """ Se ejecuta cuando la conexión se cierra """
            print("🔴 Conexión WebSocket cerrada!")

        # Iniciar la conexión WebSocket
        ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()

# Ejemplo de uso
if __name__ == "__main__":
    bingx = BingX()
    symbol = "DOGE-USDT"
    temporalidad = "1h"
    #print("Últimas velas:", bingx.get_last_candles(symbol, "1m"))

    # Iniciar WebSocket para obtener el precio en tiempo real
    bingx.get_price_stream(symbol, temporalidad)
