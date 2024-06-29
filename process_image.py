import pandas as pd
import numpy as np
import requests
from datasets import Dataset, Features, Image, Value
from huggingface_hub import HfApi
import io
from PIL import Image as PILImage
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def clean_data(df):
    # Replace NaN with appropriate values
    df['title'] = df['title'].fillna('')
    df['name'] = df['name'].fillna('')
    df['product_url'] = df['product_url'].fillna('')
    df['price'] = df['price'].fillna(0.0)
    df['original_price'] = df['original_price'].fillna(0.0)
    df['unit'] = df['unit'].fillna('')
    df['overall_rating'] = df['overall_rating'].fillna(0.0)
    df['rating_count'] = df['rating_count'].fillna(0).astype(int)
    df['image_url'] = df['image_url'].fillna('')
    
    # Remove rows with empty image_url
    df = df[df['image_url'] != '']
    
    return df

def download_image(url, max_retries=3):
    for _ in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return PILImage.open(io.BytesIO(response.content))
        except (requests.RequestException, IOError):
            time.sleep(1)
    return None

def process_batch(batch, image_col):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_row = {executor.submit(download_image, row[image_col]): row for _, row in batch.iterrows()}
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            image = future.result()
            if image:
                example = {
                    "title": row["title"],
                    "name": row["name"],
                    "product_url": row["product_url"],
                    "price": float(row["price"]),
                    "original_price": float(row["original_price"]),
                    "unit": row["unit"],
                    "overall_rating": float(row["overall_rating"]),
                    "rating_count": int(row["rating_count"]),
                    "image": image
                }
                results.append(example)
    return results

def image_dataset_from_urls(df, image_col, batch_size=1000):
    features = {
        "title": Value("string"),
        "name": Value("string"),
        "product_url": Value("string"),
        "price": Value("float32"),
        "original_price": Value("float32"),
        "unit": Value("string"),
        "overall_rating": Value("float32"),
        "rating_count": Value("int32"),
        "image": Image()
    }

    def generate_examples():
        with tqdm(total=len(df), desc="Processing images") as pbar:
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                results = process_batch(batch, image_col)
                for example in results:
                    yield example
                pbar.update(len(batch))

    return Dataset.from_generator(
        generate_examples,
        features=Features(features),
    )

def main():
    df = pd.read_csv("product_nc.csv")
    
    print("Cleaning data...")
    df = clean_data(df)
    
    print("Creating dataset...")
    dataset = image_dataset_from_urls(df, image_col="image_url")
    
    print("Pushing to Hugging Face Hub...")
    dataset.push_to_hub("Porameht/product-img-rating", private=True)
    print("Dataset uploaded successfully!")

if __name__ == "__main__":
    main()