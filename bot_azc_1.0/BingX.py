### Modulo BingX ###
import pprint
import requests
import time
import hmac
import hashlib

# Definiendo la clase BingX
class BingX:

    # Inicializa la API con las credenciales y el tipo de trading.
    def __init__(self, trade_type: str = "contractPerpetual"): # "mock" para trading simulado - contractPerpetual para trading - linearPerpetual para trading lineal
        self.api_key = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
        self.api_secret = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
        self.base_url = "https://open-api.bingx.com"
        self.trade_type = trade_type

    """ METODOS PARA OBETENER INFORMACION DE LA CUENTA Y DE LAS MONEDAS """

    # Metodo para generar la firma HMAC SHA256 requerida por la API.
    def _get_signature(self, params: str) -> str:
        return hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()

    # Metodo para obtener el balance de la cuenta
    def get_balance(self):
        timestamp = str(int(time.time() * 1000))
        params = f"timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/user/balance?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.get(url, headers=headers)
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
        return response.json()

    # Metodo para obtener informacion de la moneda
    def inf_moneda(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = requests.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract
        return None

    # Metodo para obtener el pip del precio
    def pip_precio(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = requests.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return 10 ** -contract["pricePrecision"]
        return None

    # Metodo para obtener cantidad de decimales del precio
    def cant_deci_precio(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = requests.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract["pricePrecision"]
        return None

    # Metodo para obtener pip de la moneda
    def pip_moneda(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = requests.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract["tradeMinQuantity"]
        return None

    # Metodo para obtener monto minimo USDT
    def min_usdt(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = requests.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract["tradeMinUSDT"]
        return None

    # Metodo para obtener maximo apalancamiento
    def max_apalancamiento(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/contracts"
        response = requests.get(url)
        data = response.json()
        for contract in data.get("data", []):
            if contract["symbol"] == symbol:
                return contract.get("maxLeverage", "No disponible")
        return "No disponible"

    # Metodo para conocer si existe una posicion abierta en LONG o SHORT
    def get_open_position(self, symbol: str = ""):
        timestamp = str(int(time.time() * 1000))
        params = f"timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)

        url = f"{self.base_url}/openApi/swap/v2/user/positions?{params}&signature={signature}"

        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.get(url, headers=headers)
        data = response.json()

        #pprint.pprint({"DEBUG - Respuesta API completa": data})  # 🔍 Verifica si el activo aparece en la respuesta

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

    # Metodo para obtener información de la ultima vela
    def get_last_candle(self, symbol: str, interval: str = "1m"): # intervalos definidos: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        url = f"{self.base_url}/openApi/swap/v2/quote/klines?symbol={symbol}&interval={interval}&limit=2"
        response = requests.get(url)
        #data = response.json()
        #return data["data"]
        print("DEBUG - Código de estado:", response.status_code)  # Verificar si la solicitud es exitosa
        print("DEBUG - Respuesta en texto:", response.text[:200])  # Ver los primeros 200 caracteres de la respuesta

        if response.status_code != 200:
            print("ERROR - La API devolvió un código de estado:", response.status_code)
            return {"last_candle": {}, "previous_candle": {}}

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("ERROR - No se pudo decodificar la respuesta JSON.")
            return {"last_candle": {}, "previous_candle": {}}

        if "data" not in data or len(data["data"]) < 2:
            print("DEBUG - No se encontraron suficientes datos de velas.")
            return {"last_candle": {}, "previous_candle": {}}

        return {
            "last_candle": data["data"][-1],
            "previous_candle": data["data"][-2]
        }

    def get_last_candless(self, symbol: str, interval: str = "1m"):
        """Obtiene la última y la penúltima vela del mercado."""
        url = f"{self.base_url}/openApi/swap/v2/quote/klines?symbol={symbol}&interval={interval}&limit=2"
        headers = {
            "X-BX-APIKEY": self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        print("DEBUG - Código de estado:", response.status_code)  # Verificar si la solicitud es exitosa
        print("DEBUG - Respuesta en texto:", response.text[:200])  # Ver los primeros 200 caracteres de la respuesta
        
        if response.status_code != 200:
            print("ERROR - La API devolvió un código de estado:", response.status_code)
            return {"last_candle": {}, "previous_candle": {}}
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("ERROR - No se pudo decodificar la respuesta JSON.")
            return {"last_candle": {}, "previous_candle": {}}
        
        if "data" not in data or len(data["data"]) < 2:
            print("DEBUG - No se encontraron suficientes datos de velas.")
            return {"last_candle": {}, "previous_candle": {}}
        
        return {
            "last_candle": data["data"][-1],
            "previous_candle": data["data"][-2]
        }
    

    def get_last_candles(self, symbol: str, interval: str = "1m"): # intervalos definidos: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        url = f"{self.base_url}/openApi/swap/v2/quote/klines?symbol={symbol}&interval={interval}&limit=2"
        response = requests.get(url)
        data = response.json()
        print("DEBUG - Respuesta API completa:", data)  # 🔍 Ver toda la respuesta de la API
        if "data" not in data or len(data["data"]) < 2:
            print("DEBUG - No se encontraron suficientes datos de velas.")
            return {"last_candle": {}, "previous_candle": {}}

        return {
            "last_candle": data["data"][-1],
            "previous_candle": data["data"][-2]
        }

    # Metodo para obtener el precio actual
    def get_current_price(self, symbol: str):
        url = f"{self.base_url}/openApi/swap/v2/quote/ticker/price?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        return data["data"] #["price"]


    """ METODOS PARA EJECUTAR OPERACIONES EN LA CUENTA """

    # Metodo para establecer un stop loss
    def stop_loss(self, symbol: str, cantidad: float, precio: float):
        timestamp = str(int(time.time() * 1000))
        params = f"symbol={symbol}&side=SELL&positionSide=LONG&orderType=STOP_MARKET&stopPrice={precio}&quantity={cantidad}&timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.post(url, headers=headers)
        return response.json()

    # Metodo para establecer un take profit
    def take_profit(self, symbol: str, cantidad: float, precio: float):
        timestamp = str(int(time.time() * 1000))
        params = f"symbol={symbol}&side=SELL&positionSide=LONG&orderType=TAKE_PROFIT_MARKET&stopPrice={precio}&quantity={cantidad}&timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.post(url, headers=headers)
        return response.json()

    # Metodo para crear una posicion limit
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, position_side: str):
        timestamp = str(int(time.time() * 1000))
        params = (
            f"symbol={symbol}&side={side}&positionSide={position_side}&type=LIMIT"
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
    def abrir_market(self, symbol: str, cantidad: float): #Metodo copilot
        timestamp = str(int(time.time() * 1000))
        params = f"symbol={symbol}&side=BUY&positionSide=LONG&orderType=MARKET&quantity={cantidad}&timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.post(url, headers=headers)
        return response.json()

    def place_market_order(self, symbol: str, side: str, position_side: str, quantity: float): #Metodo ChatGpt
        timestamp = str(int(time.time() * 1000))
        params = (
            f"symbol={symbol}&side={side}&positionSide={position_side}&type=MARKET"
            f"&quantity={quantity}&timestamp={timestamp}"
        )
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/trade/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}

        print("DEBUG - URL de la petición:", url)  # 🔍 Verificar la URL final generada
        response = requests.post(url, headers=headers)
        data = response.json()

        print("DEBUG - Respuesta API completa:", data)  # 🔍 Ver toda la respuesta de la API
        return data

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
    bingx = BingX()
    symbol = "DOGE-USDT"
    # Obtener información de la cuenta
    #print("La moneda es:", symbol)
    #pprint.pprint({"contract": bingx.inf_moneda(symbol)})
    #print("Margen disponible:", bingx.get_balance()["data"]["balance"]["availableMargin"]) # Margen disponible para operar
    #print("Pip del precio:", bingx.pip_precio(symbol))
    #print("Cantidad de decimales del precio:", bingx.cant_deci_precio(symbol))
    #print("Monto mínimo moneda (pip de moneda):", bingx.pip_moneda(symbol))
    #print("Monto mínimo USDT:", bingx.min_usdt(symbol))
    #print("Apalancamiento máximo:", bingx.max_apalancamiento(symbol))
    #print("\nPosición abierta:", bingx.get_open_position(symbol))
    #print("\nÚltima vela:", bingx.get_last_candles(symbol, "1m"))
    #print("\nUltima vela:", bingx.get_last_candless(symbol, "1m"))
    #print("Precio actual:", bingx.get_current_price(symbol))

    # Ejecución de ordenes
    #print("\nOrden limite:", bingx.place_limit_order(symbol, "SELL", 40, 0.16481, "SHORT"))
    
    #curl -H "X-BX-APIKEY: eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw" "https://open-api.bingx.com/openApi/swap/v2/user/balance"

