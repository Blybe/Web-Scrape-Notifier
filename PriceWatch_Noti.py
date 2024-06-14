import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from dotenv import load_dotenv
import os

#.env file (API Keys)
load_dotenv()
#Pushover API
user_key = os.getenv('USERKEY')
api_token_PRICE = os.getenv('API_PRICE')

#Urls & Max Price
alternate_url = 'https://www.alternate.nl/Razer/DeathAdder-V3-gaming-muis/html/product/1861421'
azerty_url = 'https://azerty.nl/product/razer-deathadder-v3-bk/5574144'
max_price = 70  # Max price

#Pricecheck Alternate
def check_alternate():
    try:
        response = requests.get(alternate_url)
        response.raise_for_status()  #Check for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        
        price_tag = soup.find('span', {'class': 'price'})
        if price_tag:
            alternate_price = float(price_tag.text.replace('€', '').replace(',', '.').strip())
            if alternate_price <= max_price:
                title = soup.find('h1').text.strip()
                send_notification(f"Alternate: {title} for €{alternate_price}. Link: {alternate_url}")
                print(f"Found price on Alternate: €{alternate_price}")
            else:
                print(f"Price on Alternate is too high: €{alternate_price}")
        else:
            print("Price tag not found on Alternate")
    except Exception as e:
        print(f"Error checking Alternate: {e}")

#Pricecheck Azerty
def check_azerty():
    try:
        response = requests.get(azerty_url)
        response.raise_for_status()  #Check for notice bad responses
        soup = BeautifulSoup(response.content, 'html.parser')

        #Find the price in the meta tag (Zat meer verstopt dan Alternate dus deze had not een diepere find nodig van bs4)
        price_tag = soup.find('meta', {'itemprop': 'price'})
        if price_tag:
            azerty_price = float(price_tag['content'])
            if azerty_price <= max_price:
                title = soup.find('h1').text.strip()
                send_notification(f"Azerty: {title} for €{azerty_price}. Link: {azerty_url}")
                print(f"Found price on Azerty: €{azerty_price}")
            else:
                print(f"Price on Azerty is too high: €{azerty_price}")
        else:
            print("Price tag not found on Azerty")
    except Exception as e:
        print(f"Error checking Azerty: {e}")

#Send notification via Pushover
def send_notification(message):
    payload = {
        'token': api_token_PRICE,
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

#Schedule tasks
schedule.every(1).minutes.do(check_alternate)
schedule.every(1).minutes.do(check_azerty)

#Start the user input thread
thread = threading.Thread(target=user_input_thread)
thread.daemon = True
thread.start()

#Scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
