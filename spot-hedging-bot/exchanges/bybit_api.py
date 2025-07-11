# exchanges/bybit_api.py

import requests

def get_spot_price(symbol="BTCUSDT"):
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["retCode"] == 0:
            last_price = data["result"]["list"][0]["lastPrice"]
            return float(last_price)
        else:
            print("Error from Bybit:", data)
            return None
    except requests.exceptions.Timeout:
        print("Connection to Bybit timed out.")
        return None
    except Exception as e:
        print("Exception:", e)
        return None

# Test it directly
if __name__ == "__main__":
    price = get_spot_price()
    print("BTC/USDT Spot Price from Bybit:", price)
