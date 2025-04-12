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

    # Metodo para generar la firma HMAC SHA256 requerida por la API
    def _send_request(self, method: str, endpoint: str, params: dict) -> dict:
        sorted_params = sorted(params.items())
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        timestamp = self._get_timestamp()
        params_str = f"{param_str}&timestamp={timestamp}" if param_str else f"timestamp={timestamp}"

        signature = self._get_signature(params_str)

        url = f"{self.base_url}{endpoint}?{params_str}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}

        response = requests.request(method, url, headers=headers)
        #data = response.json()
        #pprint.pprint({"DEBUG - Respuesta API": data})

        return response.json()

    # Metodo para colocar el take profit
    def set_take_profit(self, symbol: str, position_side: str, quantity: float,
                        stop_price: float, working_type: str = "CONTRACT_PRICE", order_type: str = "LIMIT") -> dict:

        side = "SELL" if position_side == "LONG" else "BUY"

        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": "TAKE_PROFIT_MARKET" if order_type == "MARKET" else "TAKE_PROFIT",
            "quantity": quantity,
            "stopPrice": stop_price,
            "workingType": working_type,
        }
        if order_type == "LIMIT":
            params["price"] = stop_price

        return self._send_request("POST", "/openApi/swap/v2/trade/order", params)

    # Metodo para colocar el stop loss
    def set_stop_loss(self, symbol: str, position_side: str, quantity: float,
                        stop_price: float, working_type: str = "CONTRACT_PRICE") -> dict:

        side = "SELL" if position_side == "LONG" else "BUY"

        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": "STOP_MARKET",
            "quantity": quantity,
            "stopPrice": stop_price,
            "workingType": working_type,
        }

        return self._send_request("POST", "/openApi/swap/v2/trade/order", params)

    # Metodo para colocar una orden de mercado o limit
    def set_limit_market_order(self, symbol: str, position_side: str, quantity: float,
                        stop_price: float = None, working_type: str = "CONTRACT_PRICE", type: str = "MARKET") -> dict:

        side = "BUY" if position_side == "LONG" else "SELL"

        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": type,
            "quantity": quantity,
            "price": stop_price,
            "workingType": working_type,
        }

        return self._send_request("POST", "/openApi/swap/v2/trade/order", params)

    # Metodo para obtener las ordenes abiertas
    def set_current_open_orders(self, symbol: str, type: str = "LIMIT") -> dict:

        params = {
            "symbol": symbol,
            "type": type,
        }

        data = self._send_request("GET", "/openApi/swap/v2/trade/openOrders", params)

        long_ordersId = []
        short_ordersId = []

        for order in data.get("data", {}).get("orders", []):
            if symbol and order.get("symbol") != symbol:
                continue
            if order.get("positionSide") == "LONG":
                long_ordersId.append(order["orderId"])
            elif order.get("positionSide") == "SHORT":
                short_ordersId.append(order["orderId"])

        print(f"🟢 Total órdenes LONG: {len(long_ordersId)}")
        print(f"🔴 Total órdenes SHORT: {len(short_ordersId)}")

        return pprint.pprint({
            "long_orders": long_ordersId,
            "short_orders": short_ordersId,
            "long_total": len(long_ordersId),
            "short_total": len(short_ordersId)
        })

    # Metodo para cancelar una orden
    def set_cancel_order(self, symbol: str, order_id: int = None):
        params = {
            "orderId": order_id, #requerido
            "symbol": symbol
        }
        return self._send_request("DELETE", "/openApi/swap/v2/trade/order", params)

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
    # Colocar SL y TP
    sl_response = bingx.set_stop_loss(
        symbol="DOGE-USDT",
        position_side="SHORT",
        quantity=40,
        stop_price=0.17920
    )
    
    # Colocar una orden de compra LIMIT
    order_short = bingx.set_limit_market_order(
        symbol="DOGE-USDT",
        position_side="SHORT",
        quantity=40,
        stop_price=0.1711,
        type="LIMIT"
    )

    order_long = bingx.set_limit_market_order(
        symbol="DOGE-USDT",
        position_side="LONG",
        quantity=40,
        stop_price=0.1400,
        type="LIMIT"
    )
    """
    
    ordenes_abiertas = bingx.set_current_open_orders(symbol)

    # Cerrar ordenes pendientes
    #cerrar_ordenes = bingx.set_cancel_order(symbol)

