import json
import requests
import time
import hmac
import hashlib
import websocket
import gzip
import io

# Definiendo constantes
URL = "wss://open-api-swap.bingx.com/swap-market"
CHANNEL = {
    "id": "e745cd6d-d0f6-4a70-8d5a-043e4c741b40",
    "reqType": "sub",
    "dataType": "BTC-USDT@kline_1m"
}

# Definiendo la clase BingX
class BingX:

    def __init__(self, trade_type: str = "contractPerpetual"):
        self.api_key = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
        self.api_secret = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
        self.base_url = "https://open-api.bingx.com"
        self.ws_url = URL
        self.trade_type = trade_type
        self.session = requests.Session()
        self.session.headers.update({
            "X-BX-APIKEY": self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.ws = None  # WebSocketApp

    """ MÉTODO PARA OBTENER PRECIO EN TIEMPO REAL USANDO WEBSOCKET """

    def on_open(self, ws):
        """Se ejecuta al abrir la conexión con WebSocket"""
        print('📡 WebSocket conectado')
        subStr = json.dumps(CHANNEL)
        ws.send(subStr)
        print(f"✅ Suscripción enviada: {subStr}")

    def on_message(self, ws, message):
        """Procesa los mensajes recibidos desde WebSocket"""
        try:
            # Descomprimir mensaje si viene en formato GZIP
            compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
            decompressed_data = compressed_data.read().decode('utf-8')

            # Convertir a JSON
            data = json.loads(decompressed_data)
            print("📩 Mensaje recibido:", data)

            # Si el servidor envía "Ping", responder con "Pong"
            if decompressed_data == "Ping":
                ws.send("Pong")
                print("🔄 Enviado: Pong")

            # Extraer el precio si está disponible
            if "data" in data and "close" in data["data"]:
                print(f"💰 Precio actual: {data['data']['close']}")

        except Exception as e:
            print("❌ Error procesando mensaje:", e)

    def on_error(self, ws, error):
        """Maneja errores en la conexión WebSocket"""
        print("⚠️ Error en WebSocket:", error)

    def on_close(self, ws, close_status_code, close_msg):
        """Se ejecuta cuando la conexión WebSocket se cierra"""
        print(f"❌ WebSocket cerrado: {close_status_code} - {close_msg}")

    def get_price_stream(self):
        """Inicia la conexión WebSocket"""
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()

# Ejemplo de uso
if __name__ == "__main__":
    bingx = BingX()

    # Iniciar WebSocket para obtener el precio en tiempo real
    bingx.get_price_stream()

#ARROJA EL DATO DEL PRECIO CON LOS DEMAS PARAMETROS Y SE DEBE MODIFICAR EL ACTIVO EN EL CHANNEL