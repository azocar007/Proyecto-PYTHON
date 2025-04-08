import pprint
import time
import requests
import hmac
import json
from hashlib import sha256

APIKEY = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
SECRETKEY = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
APIURL = "https://open-api.bingx.com"

class BingXClient:
    def __init__(self):
        self.API_URL = APIURL
        self.API_KEY = APIKEY
        self.SECRET_KEY = SECRETKEY

    def _get_sign(self, payload):
        """
        Genera la firma para la autenticación de la API.
        """
        signature = hmac.new(self.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def _parse_params(self, params_map):
        """
        Convierte un diccionario de parámetros en una cadena ordenada para firmar
        y añade el timestamp.
        """
        sorted_keys = sorted(params_map)
        params_str = "&".join(["%s=%s" % (x, params_map[x]) for x in sorted_keys])
        
        if params_str != "":
            return params_str + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return params_str + "timestamp=" + str(int(time.time() * 1000))
    
    def _send_request(self, method, path, url_params, payload={}):
        """
        Envía una solicitud a la API de BingX.
        """
        url = "%s%s?%s&signature=%s" % (self.API_URL, path, url_params, self._get_sign(url_params))
        
        headers = {
            'X-BX-APIKEY': self.API_KEY,
        }
        
        response = requests.request(method, url, headers=headers, data=payload)
        return response.json()
    
    def set_take_profit_and_stop_loss(self, symbol, position_side, tp_type, tp_price, sl_price, working_type="MARK_PRICE"):
        """
        Establece take profit y stop loss para una posición activa.
        
        Args:
            symbol (str): Par de trading (ej. "BTC-USDT")
            position_side (str): Lado de la posición ("LONG" o "SHORT")
            tp_type (str): Tipo de take profit ("LIMIT" o "MARKET")
            tp_price (float): Precio del take profit
            sl_price (float): Precio del stop loss
            working_type (str): Tipo de precio de activación ("MARK_PRICE" o "CONTRACT_PRICE")
            
        Returns:
            dict: Respuesta de la API
        """
        # Determinar el lado opuesto según la posición
        side = "SELL" if position_side == "LONG" else "BUY"
        
        # Primero establecemos el take profit
        tp_result = self.set_take_profit(symbol, position_side, tp_type, tp_price, working_type)
        
        # Luego establecemos el stop loss
        sl_result = self.set_stop_loss(symbol, position_side, sl_price, working_type)
        
        return {
            "take_profit_result": tp_result,
            "stop_loss_result": sl_result
        }
    
    def set_take_profit(self, symbol, position_side, tp_type, tp_price, working_type="MARK_PRICE"):
        """
        Establece solo el take profit para una posición activa.
        
        Args:
            symbol (str): Par de trading (ej. "BTC-USDT")
            position_side (str): Lado de la posición ("LONG" o "SHORT")
            tp_type (str): Tipo de take profit ("LIMIT" o "MARKET")
            tp_price (float): Precio del take profit
            working_type (str): Tipo de precio de activación ("MARK_PRICE" o "CONTRACT_PRICE")
            
        Returns:
            dict: Respuesta de la API
        """
        path = '/openApi/swap/v2/trade/order'
        method = "POST"
        
        # Determinar el lado opuesto según la posición
        side = "SELL" if position_side == "LONG" else "BUY"
        
        # Configurar el take profit según el tipo
        take_profit_type = "TAKE_PROFIT" if tp_type == "LIMIT" else "TAKE_PROFIT_MARKET"
        take_profit_params = {
            "type": take_profit_type,
            "stopPrice": tp_price,
            "price": tp_price,
            "workingType": working_type
        }
        
        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": "MARKET",
            "takeProfit": json.dumps(take_profit_params)
        }
        
        return self._send_request(method, path, self._parse_params(params))
    
    def set_stop_loss(self, symbol, position_side, sl_price, working_type="MARK_PRICE"):
        """
        Establece solo el stop loss para una posición activa.
        
        Args:
            symbol (str): Par de trading (ej. "BTC-USDT")
            position_side (str): Lado de la posición ("LONG" o "SHORT")
            sl_price (float): Precio del stop loss
            working_type (str): Tipo de precio de activación ("MARK_PRICE" o "CONTRACT_PRICE")
            
        Returns:
            dict: Respuesta de la API
        """
        path = '/openApi/swap/v2/trade/order'
        method = "POST"
        
        # Determinar el lado opuesto según la posición
        side = "SELL" if position_side == "LONG" else "BUY"
        
        # Configurar el stop loss (siempre a mercado)
        stop_loss_params = {
            "type": "STOP_MARKET",
            "stopPrice": sl_price,
            "price": sl_price,
            "workingType": working_type
        }
        
        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "type": "MARKET",
            "stopLoss": json.dumps(stop_loss_params)
        }
        
        return self._send_request(method, path, self._parse_params(params))


# Ejemplo de uso
if __name__ == '__main__':

    client = BingXClient()
    """
    # Ejemplo de establecer TP y SL para una posición LONG en BTC-USDT
    result = client.set_take_profit_and_stop_loss(
        symbol= "DOGE-USDT",
        position_side= "LONG",
        tp_type= "MARKET",  # "LIMIT" o "MARKET"
        tp_price= 0.17926,
        sl_price= 0.1500
    )
    print(result)

    
    #TAKE PROFIT LIMIT
    result = client.set_take_profit(
        symbol= "DOGE-USDT",
        position_side= "LONG",
        tp_type= "MARKET",  # "LIMIT" o "MARKET"
        tp_price= 0.17926
    )
    print(result)

    #TAKE PROFIT MARKET
    result = client.set_take_profit(
        symbol= "DOGE-USDT",
        position_side= "LONG",
        tp_type= "LIMIT",  # "LIMIT" o "MARKET"
        tp_price= 
    )
    print(result)
    """

    #STOP LOSS
    result = client.set_stop_loss(
        symbol= "DOGE-USDT",
        position_side= "LONG",
        sl_price= 0.150
    )
    print(result)
    