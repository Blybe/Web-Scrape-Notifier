import requests
import time
import threading
from dotenv import load_dotenv
import os

#.env file (API Keys)
load_dotenv()
#Pushover API
user_key = os.getenv('USERKEY')
api_token_TSLA = os.getenv('API_TSLA')
#Finnhub API
finnhub_api_key = os.getenv('FINNHUB_API')
finnhub_secret = os.getenv('FINNHUB_SECRET')

#Fetch Tesla stock price using Finnhub API
def fetch_tsla_price():
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol=TSLA&token={finnhub_api_key}'
        headers = {'X-Finnhub-Secret': finnhub_secret}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'c' not in data:
            raise ValueError("No data found for TSLA")
        return data['c']
    except Exception as e:
        print(f"Error fetching TSLA price: {e}")
        return None

#Check if the price is within the range
def check_price_range(price, TSLA_min_threshold, TSLA_max_threshold):
    return TSLA_min_threshold <= price <= TSLA_max_threshold

#Send notification via Pushover
def send_notification(message):
    payload = {
        'token': api_token_TSLA,
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

#Test Notifications
def user_input_thread():
    while True:
        user_input = input("Type 'test' to send a test notification: ")
        if user_input.lower() == 'test':
            send_notification("This is a Skibidi test notification.")

#Values
TSLA_min_threshold = 180  #Minimum price for notification
TSLA_max_threshold = 200  #Maximum price for notification
notification_interval = 60  #Seconds between price checks

#Test User
thread = threading.Thread(target=user_input_thread)
thread.daemon = True
thread.start()

#Program loop
while True:
    tsla_price = fetch_tsla_price()

    if tsla_price is not None and check_price_range(tsla_price, TSLA_min_threshold, TSLA_max_threshold):
        message = f"TSLA: Price is now {tsla_price:.2f}, within the range ({TSLA_min_threshold:.2f} - {TSLA_max_threshold:.2f})!"
        send_notification(message)
    
    time.sleep(notification_interval)
