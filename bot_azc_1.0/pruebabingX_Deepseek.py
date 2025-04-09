import pprint
import time
import hmac
import hashlib
from hashlib import sha256
import requests


APIKEY = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
SECRETKEY = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
APIURL = "https://open-api.bingx.com"

class BingXTrading:
    def __init__(self):
        self.api_url = APIURL
        self.api_key = APIKEY
        self.secret_key = SECRETKEY

    def _get_signature(self, payload: str) -> str:
        return hmac.new(
            self.secret_key.encode("utf-8"),
            payload.encode("utf-8"),
            digestmod=sha256
        ).hexdigest()

    def _send_request(self, method: str, endpoint: str, params: dict) -> dict:
        sorted_params = sorted(params.items())
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        timestamp = int(time.time() * 1000)
        params_str = f"{param_str}&timestamp={timestamp}" if param_str else f"timestamp={timestamp}"

        signature = self._get_signature(params_str)

        url = f"{self.api_url}{endpoint}?{params_str}&signature={signature}"
        headers = {"X-BX-APIKEY": self.api_key}

        response = requests.request(method, url, headers=headers)
        return response.json()

    def set_take_profit(self, symbol: str, position_side: str, quantity: float,
                        stop_price: float, price: float = None,
                        working_type: str = "MARK_PRICE", order_type: str = "MARKET") -> dict:
        """
        Coloca una orden de Take Profit
        :param order_type: 'MARKET' o 'LIMIT'
        """
        side = "SELL" if position_side == "LONG" else "BUY"

        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": "TAKE_PROFIT_MARKET" if order_type == "MARKET" else "TAKE_PROFIT",
            "quantity": quantity,
            "stopPrice": stop_price,
            "workingType": working_type
        }

        if order_type == "LIMIT":
            if not price:
                raise ValueError("Se requiere precio para orden LIMIT")
            params["price"] = price

        return self._send_request("POST", "/openApi/swap/v2/trade/order", params)

    def set_stop_loss(self, symbol: str, position_side: str, quantity: float,
                        stop_price: float, working_type: str = "MARK_PRICE") -> dict:
        """
        Coloca una orden de Stop Loss (siempre a mercado)
        """
        side = "SELL" if position_side == "LONG" else "BUY"

        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": "STOP_MARKET",
            "quantity": quantity,
            "stopPrice": stop_price,
            "workingType": working_type
        }

        return self._send_request("POST", "/openApi/swap/v2/trade/order", params)


if __name__ == "__main__":
    # FUNCIONA CORRECTAMENTE
    api = BingXTrading()

    """ # Take Profit a mercado
    tp_response = api.set_take_profit(
        symbol="DOGE-USDT",
        position_side="LONG",
        quantity=40,
        stop_price=0.17926,
        order_type="MARKET"
    ) """


    """ # Take Profit a límite
    tp_limit_response = api.set_take_profit(
        symbol= "DOGE-USDT",
        position_side= "LONG",
        quantity= 40,
        stop_price= 0.17926,
        price= 0.17920,
        order_type= "LIMIT"
    ) """


    # Stop Loss a mercado
    sl_response = api.set_stop_loss(
        symbol="DOGE-USDT",
        position_side="SHORT",
        quantity=40,
        stop_price=0.17920
    )    #"""