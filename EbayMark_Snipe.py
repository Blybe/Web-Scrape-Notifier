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

# Counter to limit notifications per URL
max_notifications_per_url = 2

# Global counters
marktplaats_count = 0
ebay_count = 0

# Send notification via Pushover
def send_notification(message):
    global marktplaats_count, ebay_count

    if 'Marktplaats' in message:
        marktplaats_count += 1
    elif 'eBay' in message:
        ebay_count += 1

    # Check if the maximum limit for notifications per URL is reached
    if marktplaats_count > max_notifications_per_url and ebay_count > max_notifications_per_url:
        print(f"Maximum notifications limit reached. Exiting.")
        os._exit(0)  # Exit the script

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
    global marktplaats_count
    prices_found = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('span', class_='hz-Listing-price')

        if not items:
            print(f"No items found on Marktplaats: {url}")
        
        for item in items:
            price_text = item.text.strip().replace('€', '').replace(',', '.').replace('\xa0', '')
            if price_text.isdigit() or price_text.replace('.', '', 1).isdigit():
                price = float(price_text)  # Convert to float for cents
                price = int(price) if price.is_integer() else price  # Convert to int if no cents
                if price <= max_price:
                    prices_found.append(price)
                    message = f"Found on Marktplaats: Price within range: €{price} ({url})"
                    send_notification(message)
                    if marktplaats_count >= max_notifications_per_url:
                        break  # Stop scraping Marktplaats once max notifications reached
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape Marktplaats: {e}")
    
    return prices_found

# Scrape eBay for a product
def scrape_ebay(url, max_price):
    global ebay_count
    prices_found = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('span', class_='s-item__price')

        if not items:
            print(f"No items found on eBay: {url}")
        
        for item in items:
            price_text = item.text.strip().replace('EUR', '').replace(',', '.').strip()
            if price_text.isdigit() or price_text.replace('.', '', 1).isdigit():
                price = float(price_text)  # Convert to float for cents
                price = int(price) if price.is_integer() else price  # Convert to int if no cents
                if price <= max_price:
                    prices_found.append(price)
                    message = f"Found on eBay: Price within range: €{price} ({url})"
                    send_notification(message)
                    if ebay_count >= max_notifications_per_url:
                        break  # Stop scraping eBay once max notifications reached
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape eBay: {e}")
    
    return prices_found

def job():
    print("Running scheduled job...")  # Debugging info

    # Define the URLs and max prices for each product
    products = [
        {'url': 'https://www.marktplaats.nl/q/oculus+quest+2/', 'max_price': 220},  # Oculus Quest 2
        {'url': 'https://www.ebay.nl/sch/i.html?_from=R40&_nkw=Oculus+Quest+2', 'max_price': 220},  # Oculus Quest 2
        {'url': 'https://www.marktplaats.nl/q/steelseries+apex+pro+tkl/', 'max_price': 100},  # Steelseries Apex Pro TKL
        {'url': 'https://www.ebay.nl/sch/i.html?_from=R40&_nkw=steelseries+apex+pro+tkl&_sacat=0', 'max_price': 100}  # Steelseries Apex Pro TKL
    ]

    for product in products:
        if 'marktplaats' in product['url']:
            print(f"Scraping Marktplaats: {product['url']}")  # Debugging info
            scrape_marktplaats(product['url'], product['max_price'])
        elif 'ebay' in product['url']:
            print(f"Scraping eBay: {product['url']}")  # Debugging info
            scrape_ebay(product['url'], product['max_price'])

if __name__ == "__main__":
    while True:
        job()  # Run the job function directly
        time.sleep(30)  # Wait for 30 sec
