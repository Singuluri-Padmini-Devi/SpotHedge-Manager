# exchanges/okx_api.py

import requests

def get_spot_price(symbol="BTC-USDT"):
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    try:
        response = requests.get(url, timeout=10)  # timeout added
        data = response.json()
        if data["code"] == "0":
            last_price = data["data"][0]["last"]
            return float(last_price)
        else:
            print("Error from OKX:", data)
            return None
    except requests.exceptions.Timeout:
        print("Connection to OKX timed out.")
        return None
    except Exception as e:
        print("Exception:", e)
        return None

# Test run
if __name__ == "__main__":
    price = get_spot_price()
    print("BTC/USDT Spot Price from OKX:", price)
