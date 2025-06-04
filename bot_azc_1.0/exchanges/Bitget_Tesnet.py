import requests
import time
import hmac
import hashlib
import pprint

# 🚀 API Keys de Bitget
API_KEY = "bg_9939ddadc52ea0d0472dead181813ca2"
API_SECRET = "ec2c21c06bfe077ea8c7670a07b61ac1daa9b7503a579cdc604cf3c4549ffc2c"
API_PASSPHRASE = "252020azc"

# 🔗 Endpoint base de Bitget Testnet (o cambiar a real si es mainnet)
BASE_URL = "https://api.bitget.com"

# 📌 Función para generar la firma HMAC SHA256
def generate_signature(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

# 📌 Obtener balance de la cuenta
def get_futures_balance():
    timestamp = str(int(time.time() * 1000))  # Milisegundos
    method = "GET"
    #request_path = "/api/v2/account/assets"
    #request_path = "/api/v2/spot/account/assets" 
    request_path = "/api/v2/mix/account/accounts?productType=USDT-M"

    signature = generate_signature(timestamp, method, request_path)

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}{request_path}"
    response = requests.get(url, headers=headers)

    return response.json()

# 🚀 Ejecutar la función
#balance = get_balance()
balance = get_futures_balance()

# 📊 Imprimir el resultado
#print("Status Code:", balance.get("code"))
#pprint.pprint(balance)


url = "https://api.bitget.com/api/v2/public/time"  # Endpoint público de mainnet
response = requests.get(url)

print("Status Code:", response.status_code)
print("Response Text:", response.text)

