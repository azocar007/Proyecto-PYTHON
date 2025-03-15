
import pprint
import requests
import time
import hmac
import hashlib

# 🚀 TU API KEY de BingX (CUENTA REAL)
API_KEY = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
API_SECRET = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"

# 🔗 Endpoint de la API (Mainnet)
BASE_URL = "https://open-api.bingx.com"

# 📌 Parámetros requeridos
timestamp = str(int(time.time() * 1000))
params = f"timestamp={timestamp}&tradeType=mock"  # 📌 Agregar tradeType=mock

# 🔐 Generar la firma HMAC SHA256
signature = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()

# 🔗 URL final con firma
#url = f"{BASE_URL}/openApi/swap/v2/user/balance?{params}&signature={signature}"
url = f"{BASE_URL}/openApi/swap/v2/trade/order/history?{params}&signature={signature}"

# 📨 Headers para autenticación
headers = {
    "X-BX-APIKEY": API_KEY
}

# 🚀 Hacer la solicitud GET
response = requests.get(url, headers=headers)

# 🔍 Ver resultado
pprint.pprint(f"Status Code:, {response.status_code}")

#pprint.pprint({"Response Text:", response.text})

pprint.pprint(response.json())