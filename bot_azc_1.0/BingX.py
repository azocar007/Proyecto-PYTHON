### Modulo BingX ###
import pprint
import requests
import time
import hmac
import hashlib

# Definiendo la clase BingX
class BingX:

    # Inicializa la API con las credenciales y el tipo de trading.
    def __init__(self, trade_type: str = "mock"):
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
    def get_open_position(self, symbol: str):
        timestamp = str(int(time.time() * 1000))
        params = f"timestamp={timestamp}&tradeType={self.trade_type}"
        signature = self._get_signature(params)
        url = f"{self.base_url}/openApi/swap/v2/position?{params}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}
        response = requests.get(url, headers=headers)
        data = response.json()
        position_status = {"long": False, "short": False}
        for position in data.get("data", []):
            if position["symbol"] == symbol:
                if float(position.get("positionQty", 0)) > 0:
                    position_status["long"] = True
                elif float(position.get("positionQty", 0)) < 0:
                    position_status["short"] = True
        return position_status

    """ METODOS PARA EJECUTAR OPERACIONES EN LA CUENTA """


# Ejemplo de uso
if __name__ == "__main__":
    bingx = BingX()
    symbol = "BTC-USDT"

    print("La moneda es:", symbol)
    #pprint.pprint({"contract": bingx.inf_moneda(symbol)})
    print("Margen disponible:", bingx.get_balance()["data"]["balance"]["availableMargin"]) # Margen disponible para operar
    print("Paso mínimo de precio:", bingx.pip_precio(symbol))
    print("Cantidad de decimales del precio:", bingx.cant_deci_precio(symbol))
    print("Monto mínimo moneda:", bingx.pip_moneda(symbol))
    print("Monto mínimo USDT:", bingx.min_usdt(symbol))
    print("Apalancamiento máximo:", bingx.max_apalancamiento(symbol))
    print("Posición abierta:", bingx.get_open_position(symbol))
