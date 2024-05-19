import requests
import csv
import time
import json
import argparse
from parameter_noc import params12

url = "https://nocnoc.com/buyer-service/search?b-uid=1.0.1"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer "
}
# data = {
#     "lang": "th",
#     "userType": "BUYER",
#     "locale": "th",
#     "orgIdfier": "scg",
#     "limit": 1000,
#     "page": 1,
#     "transformData": True,
#     "searchListMetaInfo": {
#         "nocNocChoiceLimit": 8,
#         "comingSoonLimit": 8,
#         "collapsedView": False
#     },
#     "abType": "A"
# }


progress_file = 'progress.json'

def save_progress(total_items, page):
    with open(progress_file, 'w') as file:
        json.dump({"total_items": total_items, "page": page}, file)

def load_progress():
    try:
        with open(progress_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"total_items": 0, "page": 1}

def write_csv(products, filename='data-nc.csv'):
    fieldnames = ["title", "name", "productUrl", "price", "originalPrice", "unit", "overallRating", "ratingCount", "image"]
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerows(products)

def fetch_page(page):
    params12["page"] = page
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=params12, timeout=10)
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                print(f"Failed to fetch page {page}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request exception on page {page}: {e}")
        time.sleep(2 ** attempt)  # Exponential backoff
    return []

def main(start_count=0, batch_size=1000, max_items=590000):
    progress = load_progress()
    total_items = progress["total_items"] if start_count == 0 else start_count
    page = progress["page"]
    
    while True:
        items = fetch_page(page)
        
        if not items:
            print(f"No more items found on page {page}.")
            break

        products = []
        for item in items:
            price_info = item.get('price', {})
            rating_info = item.get('rating', {})

            product = {
                "title": item.get('title', 'N/A'),
                "name": item.get('name', 'N/A'),
                "productUrl": item.get('productUrl', 'N/A'),
                "price": price_info.get('price', 'N/A'),
                "originalPrice": price_info.get('originalPrice', 'N/A'),
                "unit": price_info.get('unit', 'N/A'),
                "overallRating": rating_info.get('overallRating', 'N/A'),
                "ratingCount": rating_info.get('ratingCount', 'N/A'),
                "image": item.get('image', 'N/A')
            }

            products.append(product)
        
        total_items += len(items)
        
        write_csv(products)
        
        print(f"Page {page} fetched: {len(items)} items. Total items fetched: {total_items}")

        save_progress(total_items, page + 1)
        
        if total_items >= max_items:
            print(f"Reached {max_items} items limit. Stopping.")
            break

        page += 1
        time.sleep(1)  # Small delay to avoid hitting the server too hard

    print("Data fetching complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch product data from nocnoc.com and save to CSV.')
    parser.add_argument('--start_count', type=int, default=0, help='Start fetching from this product count')
    parser.add_argument('--batch_size', type=int, default=1000, help='Number of products to fetch per batch')
    parser.add_argument('--max_items', type=int, default=590000, help='Maximum number of items to fetch')

    args = parser.parse_args()
    main(start_count=args.start_count, batch_size=args.batch_size, max_items=args.max_items)
