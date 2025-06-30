import requests
import pandas as pd
import time
import random
import re
from sqlalchemy import create_engine
import schedule

# --------------------------
# 🔧 CONFIGURATION
# --------------------------

API_KEY = "add api key here "
MYSQL_USER = "add user"
MYSQL_PASS = "Add password"
MYSQL_HOST = "your host name"
MYSQL_PORT = "3306"
MYSQL_DB   = "amazon_dashboard"

# All major German cities
locations = [
    "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf", "Leipzig", "Dresden",
    "Hanover", "Nuremberg", "Bremen", "Bochum", "Bonn", "Wuppertal", "Essen", "Karlsruhe", "Mannheim",
    "Augsburg", "Wiesbaden", "Mönchengladbach", "Kiel", "Gelsenkirchen", "Chemnitz", "Freiburg", "Halle (Saale)",
    "Mainz", "Oberhausen", "Lübeck", "Erfurt", "Rostock", "Kassel", "Hagen", "Potsdam", "Saarbrücken", "Regensburg",
    "Hamm", "Heidelberg", "Würzburg", "Oldenburg", "Ingolstadt", "Paderborn", "Darmstadt", "Heilbronn", "Ulm",
    "Wolfsburg", "Reutlingen", "Göttingen", "Trier"
]

# All key Amazon.de categories
categories = {
    "Electronics": "16261631",
    "Computers & Accessories": "16262241",
    "Smart Home": "938783031",
    "Home & Kitchen": "3167641",
    "Industrial & Scientific": "5866098031",
    "Books": "186606",
    "Beauty": "870754031",
    "Clothing": "340843031",
    "Shoes & Bags": "1760297031",
    "Toys & Games": "12950651",
    "Garden & Outdoor": "10925031",
    "Sports & Outdoors": "16435121",
    "Health & Personal Care": "64030031",
    "Automotive": "78191031",
    "Pet Supplies": "340846031",
    "Grocery": "64257031",
    "Baby": "355006011"
}

# --------------------------
# 🚀 MAIN PIPELINE FUNCTION
# --------------------------
def run_pipeline():
    print("\n🔁 Starting data fetch for Amazon Germany...\n")
    all_products = []
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }

    for category_name, category_id in categories.items():
        print(f"🔍 Fetching category: {category_name}")
        for page in range(1, 4):  # limit to 3 pages per category
            url = "https://real-time-amazon-data.p.rapidapi.com/products-by-category"
            params = {
                "category_id": category_id,
                "page": str(page),
                "country": "DE"
            }

            try:
                res = requests.get(url, headers=headers, params=params)
                if res.status_code != 200:
                    print(f"❌ API error: {res.status_code} - {res.text}")
                    continue

                items = res.json().get("data", {}).get("products", [])
                for item in items:
                    asin = item.get("asin")
                    price_str = item.get("product_price", "").replace("€", "").replace(",", ".")
                    try:
                        price = float(price_str) if price_str else 0.0
                    except:
                        price = 0.0

                    currency = item.get("currency", "EUR")
                    quantity = (
                        random.randint(2, 10) if price <= 30 else
                        random.randint(1, 5) if price <= 100 else 1
                    )
                    total_sales = round(price * quantity, 2)

                    # 🔍 Fetch product description
                    description = ""
                    try:
                        detail_url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
                        detail_params = {"asin": asin, "country": "DE"}
                        detail_res = requests.get(detail_url, headers=headers, params=detail_params)
                        if detail_res.status_code == 200:
                            description = detail_res.json().get("data", {}).get("product_description", "")
                    except:
                        pass

                    all_products.append({
                        "product_id": asin,
                        "title": item.get("product_title"),
                        "category": category_name,
                        "price": price,
                        "currency": currency,
                        "quantity": quantity,
                        "total_sales": total_sales,
                        "rating": item.get("product_star_rating"),
                        "total_reviews": item.get("product_num_ratings"),
                        "is_prime": item.get("is_prime"),
                        "sales_volume": item.get("sales_volume"),
                        "delivery": item.get("delivery"),
                        "location": random.choice(locations),
                        "image_url": item.get("product_photo"),
                        "description": description,
                        "url": item.get("product_url")
                    })

                print(f"✅ Page {page}: {len(items)} products")
                time.sleep(3)

            except Exception as e:
                print(f"⚠️ Error on {category_name} page {page}: {e}")
                continue

    if not all_products:
        print("⚠️ No products collected. Skipping DB update.")
        return

    # --------------------------
    # 🧹 DATA CLEANING
    # --------------------------
    df = pd.DataFrame(all_products)

    def clean_sales_volume(text):
        if isinstance(text, str):
            match = re.search(r"(\d+)(K?)", text.replace(",", ""))
            if match:
                num = int(match.group(1))
                if "K" in match.group(2):
                    return num * 1000
                return num
        return 0

    df['sales_volume'] = df['sales_volume'].apply(clean_sales_volume)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['total_sales'] = (df['price'] * df['quantity']).round(2)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['total_reviews'] = pd.to_numeric(df['total_reviews'], errors='coerce').fillna(0).astype(int)
    df['is_prime'] = df['is_prime'].astype(str).str.upper().map({'TRUE': True, 'FALSE': False})
    df['category'] = df['category'].astype(str).str.title()
    df = df.dropna(subset=["product_id", "title"])

    # --------------------------
    # 💾 SAVE TO MYSQL
    # --------------------------
    try:
        engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
        df.to_sql(name="amazon_products_germany", con=engine, if_exists="replace", index=False)
        print("✅ Data saved to MySQL: `amazon_products_germany`")

    except Exception as e:
        print(f"❌ MySQL write failed: {e}")

# --------------------------
# ⏰ SCHEDULED RUN
# --------------------------
schedule.every(7).hours.do(run_pipeline)

print("⏳ Scheduler running... (data refresh every 7 hours)")
run_pipeline()  # Run once immediately

while True:
    schedule.run_pending()
    time.sleep(60)
