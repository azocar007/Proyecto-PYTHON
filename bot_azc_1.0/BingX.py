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

        pprint.pprint({"DEBUG - Respuesta API completa": data})  # 🔍 Verifica si el activo aparece en la respuesta

        if "data" not in data:
            print("DEBUG - No se encontró la clave 'data' en la respuesta de la API")
            return {"long": False, "short": False}
        if not data["data"]:
            print("DEBUG - La API devolvió una lista vacía, no hay posiciones abiertas.")
            return {"long": False, "short": False}

        position_status = {"long": False, "short": False}

        position = data["data"]
        for position in data.get("data", []):
            print("DEBUG - Símbolo en API:", position["symbol"], position["positionSide"], position["avgPrice"], position["positionAmt"]) # 🔍 Verifica cómo la API devuelve los símbolos de los activos
            if position["symbol"] == symbol:
                if position["positionSide"] == "LONG":
                    position_status["long"] = True
                elif position["positionSide"] == "SHORT":
                    position_status["short"] = True

        return position_status

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
    def abrir_market(self, symbol: str, cantidad: float):
        timestamp = str(int(time.time() * 1000))
        params = f"symbol={symbol}&side=BUY&positionSide=LONG&orderType=MARKET&quantity={cantidad}&timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/order?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.post(url, headers=headers)
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
    bingx = BingX()
    symbol = "DOGE-USDT"

    #print("La moneda es:", symbol)
    #pprint.pprint({"contract": bingx.inf_moneda(symbol)})
    #print("Margen disponible:", bingx.get_balance()["data"]["balance"]["availableMargin"]) # Margen disponible para operar
    #print("Paso mínimo de precio:", bingx.pip_precio(symbol))
    #print("Cantidad de decimales del precio:", bingx.cant_deci_precio(symbol))
    #print("Monto mínimo moneda:", bingx.pip_moneda(symbol))
    #print("Monto mínimo USDT:", bingx.min_usdt(symbol))
    #print("Apalancamiento máximo:", bingx.max_apalancamiento(symbol))
    
    # Colocar una orden de compra
    #print("\nOrden limite:", bingx.place_limit_order(symbol, "SELL", 40, 0.16481, "SHORT"))
    #print("\nPosición abierta:", bingx.get_open_position(symbol))
    print("\nPosición abierta:", bingx.get_open_position())



    """
    'DEBUG - Respuesta API completa': {'code': 0,
                                    'data': [{'availableAmt': '40',
                                              'avgPrice': '0.16481',
                                              'createTime': 1742308488000,
                                              'currency': 'USDT',
                                              'initialMargin': '0.3296',
                                              'isolated': False,
                                              'leverage': 20,
                                              'liquidationPrice': 0,
                                              'margin': '0.1387',
                                              'markPrice': '0.16958',
                                              'maxMarginReduction': '0.0000',
                                              'onlyOnePosition': False,
                                              'pnlRatio': '-0.5793',
                                              'positionAmt': '40',
                                              'positionId': '1902005772926275584',
                                              'positionSide': 'SHORT',
                                              'positionValue': '6.78337',
                                              'realisedProfit': '0.0006',
                                              'riskRate': '0.0022',
                                              'symbol': 'DOGE-USDT',
                                              'unrealizedProfit': '-0.1910',
                                              'updateTime': 1742371214386},
                                             {'availableAmt': '40',
                                              'avgPrice': '0.16421',
                                              'createTime': 1742307837000,
                                              'currency': 'USDT',
                                              'initialMargin': '0.3284',
                                              'isolated': False,
                                              'leverage': 20,
                                              'liquidationPrice': 0,
                                              'margin': '0.5434',
                                              'markPrice': '0.16958',
                                              'maxMarginReduction': '0.0000',
                                              'onlyOnePosition': False,
                                              'pnlRatio': '0.6545',
                                              'positionAmt': '40',
                                              'positionId': '1902003039821320192',
                                              'positionSide': 'LONG',
                                              'positionValue': '6.78337',
                                              'realisedProfit': '-0.0052',
                                              'riskRate': '0.0022',
                                              'symbol': 'DOGE-USDT',
                                              'unrealizedProfit': '0.2150',
                                              'updateTime': 1742371214538}],
                                    'msg': ''}}
DEBUG - Símbolo en API: DOGE-USDT SHORT
DEBUG - Símbolo en API: DOGE-USDT LONG

Posición abierta: {'long': False, 'short': False}
"""