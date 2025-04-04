### Modulo BingX ###
import pprint
import time
import threading
import hmac
import hashlib
import json
import gzip
import io
import websocket
import requests


# Definiendo la clase BingX
class BingX:

    # Iniciando variables del diccionario de entrada
    # Inicializa la API con las credenciales y el tipo de trading.
    def __init__(self, dict: dict):
        self.api_key = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
        self.api_secret = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
        self.trade_type = "contractPerpetual"
        self.session = requests.Session()
        self.session.headers.update({
            "X-BX-APIKEY": self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.base_url = "https://open-api.bingx.com"
        self.ws_url = "wss://open-api-swap.bingx.com/swap-market"
        self.last_price = None
        self.ws = None
        self.ws_running = False  # Controla si el WebSocket está activo
        self.dict = dict
        self.entrada_long = self.dict["LONG"]
        self.entrada_short = self.dict["SHORT"]


    """ METODOS PARA OBETENER INFORMACION DE LA CUENTA Y DE LAS MONEDAS """

    # Metodo para generar la firma HMAC SHA256 requerida por la API.
    def _get_signature(self, params: str) -> str:
        return hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()

    # Metodo para obtener el timestamp actual.
    def _get_timestamp(self) -> str:
        return str(int(time.time() * 1000))

    # Metodo para obtener el balance de la cuenta
    def get_balance(self):
        timestamp = self._get_timestamp()
        params = f"timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/user/balance?{params}&signature={signature}"
        response = self.session.get(url)
        """
        A continuación se muestra la información que se puede obtener en el dict "balance":
        asset →             El activo de la cuenta (USDT).
        availableMargin →   Lo que puedes usar para operar.
        balance →           Todo tu saldo de la cuenta.
        equity →            Tu balance total incluyendo ganancias/pérdidas abiertas.
        freezedMargin →     Cuánto de tu saldo está congelado.
        realisedProfit →    Las ganancias/perdidas que ya cerraste.
        shortUid →          Tu ID de usuario.
        unrealizedProfit →  Si tienes posiciones abiertas, muestra cuánto has ganado o perdido.
        usedMargin →        Cuánto de tu saldo está en uso como margen.
        userId →            Tu ID de usuario.
        """
        return response.json()["data"]["balance"]

    # Metodo para obtener informacion de la moneda
    def inf_moneda(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = self.session.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract
        return None

    # Metodo para obtener el pip del precio
    def pip_precio(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = self.session.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return 10 ** -contract["pricePrecision"]
        return None

    # Metodo para obtener cantidad de decimales del precio
    def cant_deci_precio(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = self.session.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract["pricePrecision"]
        return None

    # Metodo para obtener pip de la moneda
    def pip_moneda(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = self.session.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract["tradeMinQuantity"]
        return None

    # Metodo para obtener monto minimo USDT
    def min_usdt(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = self.session.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract["tradeMinUSDT"]
        return None

    # Metodo para obtener maximo apalancamiento, por el momemnto no funciona
    def max_apalancamiento(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts" #"/openApi/swap/v2/trade/leverage" 
        response = self.session.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract.get("maxLeverage", "No disponible")
        return "No disponible"

    # Metodo para conocer si existe una posicion abierta en LONG o SHORT
    def get_open_position(self, symbol: str = ""):
        timestamp = self._get_timestamp()
        params = f"timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/user/positions?{params}&signature={signature}"
        response = self.session.get(url)
        data = response.json()
        #pprint.pprint({"DEBUG - Respuesta API completa": data["data"]})  # 🔍 Verifica si el activo aparece en la respuesta

        long_position = {}
        short_position = {}

        if "data" not in data or not data["data"]:
            print("DEBUG - No hay posiciones abiertas.")
            return {"long": long_position, "short": short_position}

        for position in data["data"]:
            #pprint.pprint({"DEBUG - Datos de posición": position})  # 🔍 Verifica cómo la API devuelve los datos
            if position["symbol"] == symbol:
                if position["positionSide"] == "LONG": #float(position.get("positionAmt", 0)) > 0 and 
                    long_position = {
                        "avgPrice": position.get("avgPrice", "N/A"),
                        "positionAmt": position.get("positionAmt", "N/A")
                    }
                elif position["positionSide"] == "SHORT": #float(position.get("positionAmt", 0)) > 0 and 
                    short_position = {
                        "avgPrice": position.get("avgPrice", "N/A"),
                        "positionAmt": position.get("positionAmt", "N/A")
                    }
        return {"long": long_position, "short": short_position}

    # Metodo para monitorear las posiciones de un activo en tiempo.
    def monitor_open_positions(self, symbol: str = ""):
        MAX_REQUESTS_PER_MINUTE = 60
        request_count = 0
        start_time = time.time()

        while True:
            # Control de límite de peticiones por minuto
            if request_count >= MAX_REQUESTS_PER_MINUTE:
                elapsed_time = time.time() - start_time
                if elapsed_time < 60:
                    sleep_time = 60 - elapsed_time
                    print(f"⏳ Esperando {sleep_time:.2f} segundos para evitar bloqueos...")
                    time.sleep(sleep_time)
                request_count = 0
                start_time = time.time()

            try:
                positions = self.get_open_position(symbol)  # Llamada a la API
                print(f"📊 Posiciones abiertas: {positions}")

                request_count += 1
            except Exception as e:
                print(f"❌ Error obteniendo posiciones: {e}")

            time.sleep(2)  # Intervalo de 5 segundos para no saturar la API

    # Metodo para obtener información de la ultima vela
    def get_last_candles(self, symbol: str = "BTC-USDT", interval: str = "1m", limit: int = 2):
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

    # Metodo para obtener el precio en tiempo real con websocket
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
                    self.check_strategy(self.last_price) # Ejecuta la estrategia en tiempo real

            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")

        def on_error(ws, error):
            print(f"⚠️ Error en WebSocket: {error}")
            self.ws_running = False  # Marcar WebSocket como inactivo
            self.__reconnect(symbol, interval)

        def on_close(ws, close_status_code, close_msg):
            print("🔴 Conexión WebSocket cerrada. Intentando reconectar...")
            self.ws_running = False  # Marcar WebSocket como inactivo
            self.__reconnect(symbol, interval)

        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.ws.run_forever() # self.ws.run_forever(ping_interval=30)  # Envia Ping cada 30 segundos

    # Metodo para realizar la reconeción de la websocket
    def __reconnect(self, symbol: str = "BTC-USDT", interval: str = "1m"):
        """ Intenta reconectar el WebSocket después de 5 segundos """
        time.sleep(5)
        print("♻️ Reintentando conexión...")
        threading.Thread(target=self.start_websocket, args=(symbol, interval)).start()

    # Estrategia de entrada al mercado
    def check_strategy(self, last_price):
        """
        Aquí defines la lógica de trading.
        :param last_price: Último precio recibido.
        """
        # Configurar un umbral de compra y venta
        if last_price <= float(self.entrada_long):
            print("📉 Precio bajo detectado. Oportunidad de COMPRA 💰")
            # Aquí puedes llamar a un método para abrir una orden de compra
        elif last_price >= float(self.entrada_short):
            print("📈 Precio alto detectado. Oportunidad de VENTA 🔥")
            # Aquí puedes llamar a un método para cerrar la operación


    """ METODOS PARA EJECUTAR OPERACIONES EN LA CUENTA """


    # Metodo para crear una posicion limit
    def place_limit_market_order(self, data: dict)-> dict:

        symbol: str = data["symbol"]
        side: str = data["side"]
        quantity: float = data["quantity"]
        price: float = data["price"]
        position_side: str = data["position_side"]
        tipe: str = data["type"]

        timestamp = str(int(time.time() * 1000))
        params = (
            f"symbol={symbol}&side={side}&positionSide={position_side}&type={tipe}"
            f"&quantity={quantity}&price={price}&timestamp={timestamp}&tradeType={self.trade_type}"
        )
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/trade/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.post(url, headers=headers)
        print("DEBUG - Código de estado:", response.status_code)
        print("DEBUG - Respuesta API:", response.json())
        """"
        Ejemplos de uso:
        positionSide="LONG" con side="BUY" → Abre una posición larga.
        positionSide="LONG" con side="SELL" → Cierra una posición larga.
        positionSide="SHORT" con side="SELL" → Abre una posición corta.
        positionSide="SHORT" con side="BUY" → Cierra una posición corta.
        """
        return response.json()

    # Metodo para abrir una posicion market
    def set_sl_tp(self, data: dict) -> dict:
        """
        Establece Stop Loss (SL) y Take Profit (TP) en una orden abierta.

        Parámetros en `data`:
        - symbol (str): Activo a operar (ej: "DOGE-USDT").
        - position_side (str): "LONG" o "SHORT".
        - stop_loss (float): Precio para Stop Loss (opcional).
        - take_profit (float): Precio para Take Profit (opcional).
        - take_profit_type (str): "MARKET" o "LIMIT" (predeterminado: "MARKET").
        - tp_price (float): Precio para Take Profit si es LIMIT (opcional).
        - quantity (float): Cantidad de monedas a cerrar en TP/SL (opcional).

        Retorna:
        - dict con la respuesta de la API.
        """

        symbol: str = data["symbol"]
        position_side: str = data["position_side"]
        stop_loss: float = data.get("stop_loss", 0)
        take_profit: float = data.get("take_profit", 0)
        take_profit_type: str = data.get("take_profit_type", "MARKET")  # "MARKET" o "LIMIT"
        tp_price: float = data.get("tp_price", 0)  # Precio TP si es LIMIT
        quantity: float = data.get("quantity", 0)  # Cantidad a cerrar

        timestamp = str(int(time.time() * 1000))

        params = f"symbol={symbol}&positionSide={position_side}&timestamp={timestamp}&tradeType={self.trade_type}"

        if stop_loss > 0:
            sl_payload = {
                "type": "STOP_MARKET",
                "stopPrice": stop_loss,
                "workingType": "MARK_PRICE"
            }
            if quantity > 0:
                sl_payload["quantity"] = quantity
            params += f"&stopLoss={json.dumps(sl_payload)}"

        if take_profit > 0:
            tp_payload = {
                "type": f"TAKE_PROFIT_{take_profit_type}",
                "stopPrice": take_profit,
                "workingType": "MARK_PRICE"
            }
            if take_profit_type == "LIMIT" and tp_price > 0:
                tp_payload["price"] = tp_price
            if quantity > 0:
                tp_payload["quantity"] = quantity
            params += f"&takeProfit={json.dumps(tp_payload)}"

        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/trade/order/algo?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}

        response = requests.post(url, headers=headers)

        print("DEBUG - Código de estado:", response.status_code)
        print("DEBUG - Respuesta API:", response.json())

        return response.json()

    # Metodo para cancelar una orden
    def cancel_order(self, symbol: str, order_id: str):
        timestamp = str(int(time.time() * 1000))
        params = f"symbol={symbol}&orderId={order_id}&timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.delete(url, headers=headers)
        return response.json()


# Ejemplo de uso
if __name__ == "__main__":
    symbol = "DOGE-USDT"
    temporalidad = "1h"
    entradas = {
        "LONG": 0.1900,
        "SHORT": 0.180
        }

    # Obtener información de la cuenta
    bingx = BingX(entradas)
    #print("Balance de la cuenta:", bingx.get_balance()["availableMargin"]) # Margen disponible para operar
    #pprint.pprint({"Activo": symbol, "Información" : bingx.inf_moneda(symbol)})
    #print("Pip del precio:", bingx.pip_precio(symbol))
    #print("Cantidad de decimales del precio:", bingx.cant_deci_precio(symbol))
    #print("Monto mínimo moneda (pip de moneda):", bingx.pip_moneda(symbol))
    #print("Monto mínimo USDT:", bingx.min_usdt(symbol))
    #print("Apalancamiento máximo:", bingx.max_apalancamiento(symbol))

    #print("\nPosición abierta:", bingx.get_open_position(symbol))
    #bingx.monitor_open_positions(symbol)
    #pprint.pprint({"Ultima vela cerrada del activo": bingx.get_last_candles(symbol, "5m")[1]})
    #bingx.start_websocket(symbol, temporalidad)
    """
    while True:     # Bucle principal para monitorear el último precio sin abrir múltiples conexiones
        time.sleep(5)
        if bingx.last_price is not None:
            print(f"🔄 Último precio disponible: {bingx.last_price}")
        else:
            print("⏳ Esperando datos de precio...")
    #"""
    #bingx.place_limit_order(symbol, "BUY", 40, 0.16201, "LONG")

    # Diccionario de datos para la orden
    data = {
        "symbol": "DOGE-USDT",
        "side": "BUY",
        "position_side": "LONG",
        "quantity": 40,
        "price": 0.16481,
        "type": "LIMIT"
    }

    # Ejecución de ordenes
    pprint.pprint({"Orden limite": bingx.place_limit_market_order(data)})


"""
RESPUESTA DE LA API PARA UNA ORDEN LIMIT CREADA CORRECTAMENTE
{'Orden limite': {'code': 0,
                'data': {'order': {'activationPrice': 0,
                                'avgPrice': '0.00000',
                                'clientOrderID': '',
                                'clientOrderId': '',
                                'closePosition': '',
                                'orderID': '1906525481205977088',
                                'orderId': 1906525481205977088,  
                                'positionSide': 'LONG',
                                'price': 0.16481,
                                'priceRate': 0,
                                'quantity': 40,
                                'reduceOnly': False,
                                'side': 'BUY',
                                'status': 'NEW',
                                'stopGuaranteed': '',
                                'stopLoss': '',
                                'stopPrice': 0,
                                'symbol': 'DOGE-USDT',
                                'takeProfit': '',
                                'timeInForce': 'GTC',
                                'type': 'LIMIT',
                                'workingType': 'MARK_PRICE'}},
                'msg': ''}}
"""
"""
                data":{"order":{"orderId":1906862775624486912,
                                "orderID":"1906862775624486912",
                                "symbol":"DOGE-USDT",
                                "positionSide":"LONG",
                                "side":"BUY",
                                "type":"LIMIT",
                                "price":0.16481,
                                "quantity":40,
                                "stopPrice":0,
                                "workingType":"MARK_PRICE",
                                "clientOrderID":"",
                                "clientOrderId":"",
                                "timeInForce":"GTC",
                                "priceRate":0,
                                "stopLoss":"",
                                "takeProfit":"",
                                "reduceOnly":false,
                                "activationPrice":0,
                                "closePosition":"",
                                "stopGuaranteed":"",
                                "status":"NEW",
                                "avgPrice":"0.00000"}}}'}

"""