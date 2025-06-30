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

# Amazon categories to scrape
categories = {
    "Electronics": "172282",
    "Computers": "541966",
    "Smart Home": "6563140011",
    "Arts & Crafts": "2617941011",
    "Men's Fashion": "7147440011",
    "Women's Fashion": "7141123011",
    "Home & Kitchen": "1055398",
    "Industrial": "16310091"
}

locations = [
    "New York", "San Francisco", "Chicago", "Houston",
    "Miami", "Denver", "Seattle", "Boston", "Los Angeles"
]

# --------------------------
# 🚀 MAIN PIPELINE FUNCTION
# --------------------------
def run_pipeline():
    print("\n🔁 Starting scheduled fetch + clean + MySQL store...\n")

    all_products = []
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }

    for category_name, category_id in categories.items():
        print(f"🔍 Fetching: {category_name}")
        for page in range(1, 6):  # 5 pages per category
            url = "https://real-time-amazon-data.p.rapidapi.com/products-by-category"
            params = {
                "category_id": category_id,
                "page": str(page),
                "country": "US"
            }

            try:
                res = requests.get(url, headers=headers, params=params)
                if res.status_code != 200:
                    print(f"❌ API error: {res.status_code} - {res.text}")
                    continue

                items = res.json().get("data", {}).get("products", [])
                for item in items:
                    asin = item.get("asin")
                    price_str = item.get("product_price", "").replace("$", "").replace(",", "")
                    try:
                        price = float(price_str) if price_str else 0.0
                    except:
                        price = 0.0

                    currency = item.get("currency", "USD")

                    # Quantity logic
                    if price <= 30:
                        quantity = random.randint(2, 10)
                    elif price <= 100:
                        quantity = random.randint(1, 5)
                    else:
                        quantity = 1

                    total_sales = round(price * quantity, 2)

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
                        "url": item.get("product_url")
                    })

                print(f"✅ Page {page}: {len(items)} products")
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ Error on {category_name} page {page}: {e}")
                continue

    if not all_products:
        print("⚠️ No products collected. Skipping DB update.")
        return

    # 🧹 Data Cleaning
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

    # 🗃️ Store to MySQL
    try:
        engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
        df.to_sql(name="amazon_products", con=engine, if_exists="replace", index=False)
        print("✅ Cleaned data saved to MySQL table: `amazon_products`")

    except Exception as e:
        print(f"❌ MySQL write failed: {e}")

# --------------------------
# ⏰ Scheduler Setup (every hour)
# --------------------------
schedule.every(6).hours.do(run_pipeline)

print("⏳ Scheduler running... will fetch and update every hour.")
run_pipeline()  # Run once at start

while True:
    schedule.run_pending()
    time.sleep(60)
