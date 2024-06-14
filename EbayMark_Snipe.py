import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
import os

#Load API keys from .env file
load_dotenv()
user_key = os.getenv('USERKEY')
api_token_PRICE = os.getenv('API_PRICE')

#Maximum notifications per URL
max_notifications_per_url = 2

#Counters for notifications
marktplaats_counts = {
    'oculus': 0,
    'apex_pro': 0
}
ebay_counts = {
    'oculus': 0,
    'apex_pro': 0
}

#Send notification via Pushover
def send_notification(message, url):
    global marktplaats_counts, ebay_counts

    if 'Marktplaats' in message:
        if 'oculus' in url:
            marktplaats_counts['oculus'] += 1
        elif 'apex_pro' in url:
            marktplaats_counts['apex_pro'] += 1
    elif 'eBay' in message:
        if 'oculus' in url:
            ebay_counts['oculus'] += 1
        elif 'apex_pro' in url:
            ebay_counts['apex_pro'] += 1

    #Check if the maximum limit for notifications per URL is reached
    if (marktplaats_counts['oculus'] >= max_notifications_per_url and
        marktplaats_counts['apex_pro'] >= max_notifications_per_url and
        ebay_counts['oculus'] >= max_notifications_per_url and
        ebay_counts['apex_pro'] >= max_notifications_per_url):
        print(f"Maximum notifications limit reached for all URLs. Exiting.")
        os._exit(0)  #Exit

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

#Marktplaats Scraper
def scrape_marktplaats(url, max_price, product_type):
    global marktplaats_counts
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
                price = float(price_text) #Convert to float for cents
                price = int(price) if price.is_integer() else price #Convert to int if no cents
                if price <= max_price:
                    prices_found.append(price)
                    message = f"Found on Marktplaats: Price within range: €{price} ({url})"
                    send_notification(message, product_type)
                    if marktplaats_counts[product_type] >= max_notifications_per_url:
                        break #max notifications reached
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape Marktplaats: {e}")
    
    return prices_found

#eBay Scraper
def scrape_ebay(url, max_price, product_type):
    global ebay_counts
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
                price = float(price_text)  #Convert to float for cents
                price = int(price) if price.is_integer() else price  #Convert to int if no cents
                if price <= max_price:
                    prices_found.append(price)
                    message = f"Found on eBay: Price within range: €{price} ({url})"
                    send_notification(message, product_type)
                    if ebay_counts[product_type] >= max_notifications_per_url:
                        break  #max notifications reached
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape eBay: {e}")
    
    return prices_found

def job():
    print("Running scheduled job...")

    #The URLs and max prices
    products = [
        {'url': 'https://www.marktplaats.nl/q/oculus+quest+2/', 'max_price': 220, 'type': 'oculus'},  # Oculus Quest 2 on Marktplaats
        {'url': 'https://www.ebay.nl/sch/i.html?_from=R40&_nkw=Oculus+Quest+2', 'max_price': 220, 'type': 'oculus'},  # Oculus Quest 2 on eBay
        {'url': 'https://www.marktplaats.nl/q/steelseries+apex+pro+tkl/', 'max_price': 100, 'type': 'apex_pro'},  # Steelseries Apex Pro TKL on Marktplaats
        {'url': 'https://www.ebay.nl/sch/i.html?_from=R40&_nkw=steelseries+apex+pro+tkl&_sacat=0', 'max_price': 100, 'type': 'apex_pro'}  # Steelseries Apex Pro TKL on eBay
    ]

    for product in products:
        if 'marktplaats' in product['url']:
            print(f"Scraping Marktplaats: {product['url']}")
            scrape_marktplaats(product['url'], product['max_price'], product['type'])
        elif 'ebay' in product['url']:
            print(f"Scraping eBay: {product['url']}")
            scrape_ebay(product['url'], product['max_price'], product['type'])

if __name__ == "__main__":
    while True:
        job() #Run the job function directly
        time.sleep(30) #30 sec waittimer
