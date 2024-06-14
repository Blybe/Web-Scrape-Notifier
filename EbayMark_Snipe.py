import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()
user_key = os.getenv('USERKEY')
api_token_PRICE = os.getenv('API_PRICE')

# Send notification via Pushover
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

# Scrape Marktplaats for a product
def scrape_marktplaats(url, max_price):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='mp-Listing')

        for item in items:
            title_tag = item.find('a', class_='mp-Listing-title')
            price_tag = item.find('span', class_='mp-Listing-price')
            
            if title_tag and price_tag:
                title = title_tag.text.strip()
                price_text = price_tag.text.strip().replace('€', '').replace(',', '').replace('.', '')
                if price_text.isdigit():
                    price = int(price_text)
                    if price <= max_price:
                        message = f"Found on Marktplaats: {title} for €{price} ({url})"
                        send_notification(message)
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape Marktplaats: {e}")

# Scrape eBay for a product
def scrape_ebay(url, max_price):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='s-item')

        for item in items:
            title_tag = item.find('h3', class_='s-item__title')
            price_tag = item.find('span', class_='s-item__price')
            
            if title_tag and price_tag:
                title = title_tag.text.strip()
                price_text = price_tag.text.strip().replace('€', '').replace(',', '').replace('.', '')
                price_text = ''.join(filter(str.isdigit, price_text))  # Keep only digits
                if price_text.isdigit():
                    price = int(price_text)
                    if price <= max_price:
                        message = f"Found on eBay: {title} for €{price} ({url})"
                        send_notification(message)
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape eBay: {e}")

# Scheduled job to scrape websites
def job():
    # Define the URLs and max prices for each product
    products = [
        {'url': 'https://www.marktplaats.nl/q/oculus+quest+2/', 'max_price': 220},  #Oculus Quest 2
        {'url': 'https://www.ebay.nl/sch/i.html?_from=R40&_nkw=Oculus+Quest+2', 'max_price': 220},  #Oculus Quest 2
        {'url': 'https://www.marktplaats.nl/q/steelseries+apex+pro+tkl/', 'max_price': 100},  #Steelseries Apex Pro TKL
        {'url': 'https://www.ebay.nl/sch/i.html?_from=R40&_nkw=steelseries+apex+pro+tkl&_sacat=0', 'max_price': 100}  #Steelseries Apex Pro TKL
    ]

    for product in products:
        if 'marktplaats' in product['url']:
            scrape_marktplaats(product['url'], product['max_price'])
        elif 'ebay' in product['url']:
            scrape_ebay(product['url'], product['max_price'])

# Schedule the job to run every minute
schedule.every(1).minute.do(job)

# Run the scheduler in a separate thread to allow it to run continuously
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()
