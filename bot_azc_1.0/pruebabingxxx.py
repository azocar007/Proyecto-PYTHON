import time
import requests
import hmac
import hashlib

API_KEY = "eQIiQ5BK4BGJJNgAce6QPN3iZRtjVUuo5NgVP2lnbe5xgywXr0pjP3x1tWaFnqVmavHXLRjFYOlg502XxkcKw"
API_SECRET = "OkIfPdSZOG1nua7UI7bKfbO211T3eS21XVwBymT8zg84lAwmrjtcDnZKfAd7dPJVuATTUe3ibzUwaWxTuCLw"
BASE_URL = "https://open-api.bingx.com"
MAX_REQUESTS_PER_MINUTE = 60

def get_open_positions():
    request_count = 0
    start_time = time.time()

    while True:
        if request_count >= MAX_REQUESTS_PER_MINUTE:
            elapsed_time = time.time() - start_time
            if elapsed_time < 60:
                sleep_time = 60 - elapsed_time
                print(f"⏳ Esperando {sleep_time:.2f} segundos para evitar bloqueos...")
                time.sleep(sleep_time)
            request_count = 0
            start_time = time.time()

        try:
            endpoint = "/openApi/swap/v2/position"
            timestamp = int(time.time() * 1000)
            sign_str = f"timestamp={timestamp}".encode()
            signature = hmac.new(API_SECRET.encode(), sign_str, hashlib.sha256).hexdigest()
            
            headers = {"X-BX-APIKEY": API_KEY}
            params = {"timestamp": timestamp, "signature": signature}

            response = requests.get(BASE_URL + endpoint, headers=headers, params=params)
            data = response.json()

            if data.get("code") == 0:
                print(f"📊 Posiciones abiertas: {data['data']}")
            else:
                print(f"⚠️ Error en API: {data}")

            request_count += 1
        except Exception as e:
            print(f"❌ Error obteniendo posiciones: {e}")

        time.sleep(5)  # Consulta cada 5 segundos (12 peticiones por minuto)

get_open_positions()



# 🔥 INICIAR EL WEBSOCKET 🔥
