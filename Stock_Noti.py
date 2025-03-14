import requests
import time
import threading
from dotenv import load_dotenv
import os

#.env file (API Keys)
load_dotenv()
#Pushover API
user_key = os.getenv('USERKEY')
api_token_STOCK = os.getenv('API_STOCK')
#Finnhub API
finnhub_api_key = os.getenv('FINNHUB_API')
finnhub_secret = os.getenv('FINNHUB_SECRET')

#Fetch Finnhub API
def fetch_stock_price(symbol):
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_api_key}'
        headers = {'X-Finnhub-Secret': finnhub_secret}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'c' not in data:
            raise ValueError(f"No data found for {symbol}")
        print(f"Fetched price for {symbol}: {data['c']}")
        return data['c']
    except Exception as e:
        print(f"Error fetching {symbol} price: {e}")
        return None

#Price within the range
def check_price_range(price, min_threshold, max_threshold):
    return min_threshold <= price <= max_threshold

#Send noti via Pushover
def send_notification(message):
    payload = {
        'token': api_token_STOCK,
        'user': user_key,
        'message': message,
        'title': 'Price Alert'
    }
    try:
        response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
        response.raise_for_status()
        print("Notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")

#Values Stocks
stock_thresholds = {
    'TSLA': {'min': 180, 'max': 200},
    'GME': {'min': 20, 'max': 40},
    'NVDA': {'min': 120, 'max': 140},
    'ASML': {'min': 1000, 'max': 1200},
    'INTC': {'min': 30, 'max': 40}
}
notification_interval = 60  #Seconds 

#Program loop
while True:
    for symbol, thresholds in stock_thresholds.items():
        price = fetch_stock_price(symbol)
        if price is not None:
            print(f"{symbol} price: {price}")
            if check_price_range(price, thresholds['min'], thresholds['max']):
                message = f"{symbol}: Price is now {price:.2f}, within the range ({thresholds['min']:.2f} - {thresholds['max']:.2f})!"
                print(f"Sending notification for {symbol}")
                send_notification(message)
            else:
                print(f"{symbol} price {price} is out of range ({thresholds['min']} - {thresholds['max']})")
    
    time.sleep(notification_interval)
