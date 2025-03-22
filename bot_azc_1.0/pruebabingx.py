### ENSAYOS DE LA API DE BING X CODIGOS DE LA PAGINA ###
import pprint
import time
import requests
import hmac
from hashlib import sha256

APIURL = "https://open-api.bingx.com"
APIKEY = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
SECRETKEY = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"

# Obtener velas
def demo():
    payload = {}
    path = '/openApi/swap/v3/quote/klines'
    method = "GET"
    paramsMap = {
    "symbol": "DOGE-USDT",
    "interval": "1h",
    "limit": "1", # cantidad de velas
    "startTime": "" #"1702717199998" # Fecha de inicio en milisegundos
}
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    #print("sign=" + signature)
    return signature


def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    #print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.text

def parseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    if paramsStr != "": 
        return paramsStr+"&timestamp="+str(int(time.time() * 1000))
    else:
        return paramsStr+"timestamp="+str(int(time.time() * 1000))

trade_type: str = "contractPerpetual"

if __name__ == '__main__':
    print(type(demo()))
    pprint.pprint({"Informaciòn de velas": demo()["data"]})




"""
{'demo': '{"code":0,"msg":"","data":[{
"contractId":"100",
"symbol":"BTC-USDT",
"size":"0.0001",
"quantityPrecision":4,
"pricePrecision":1,
"feeRate":0.0005,
"makerFeeRate":0.0002,
"takerFeeRate":0.0005,
"tradeMinLimit":0,
"tradeMinQuantity":0.0001,
"tradeMinUSDT":2,
"currency":"USDT",
"asset":"BTC",
"status":1,
"apiStateOpen":"true",
"apiStateClose":"true",
"ensureTrigger":true,
"triggerFeeRate":"0.00050000",
"brokerState":false,
"launchTime":1586275200000,
"maintainTime":0,
"offTime":0}
"""