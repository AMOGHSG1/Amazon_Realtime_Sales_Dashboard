#  Realtime Amazon Sales Dashboard 
<p align="left">
  <img src="https://github.com/user-attachments/assets/0ef2d300-56ee-4ac8-9bce-4782902c0a51" alt="amazon-logo" width="200"/>
</p>




A real-time data analytics pipeline and interactive dashboard that monitors Amazon product performance using the RapidAPI Amazon Real-Time Data API, Python for data processing, MySQL for storage, and Tableau for visualization.

---

## 🚀 Overview

This project automates the extraction, transformation, and visualization of Amazon product listings across multiple categories. It collects product data using the RapidAPI Amazon API, processes and stores it in MySQL, and presents insights in an interactive Tableau dashboard.

---

> ![image](https://github.com/user-attachments/assets/2cb65881-d477-4a75-919a-54dca8b20480)


## 🛠️ Tech Stack

- **Data Source**: [RapidAPI - Real-Time Amazon Data API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)
- **Backend**: Python (`requests`, `pandas`, `sqlalchemy`, `schedule`)
- **Database**: MySQL
- **Visualization**: Tableau
- **Automation**: Python `schedule` module (6-hour interval)

---

## 🔌 API Endpoints Used

| Endpoint               | Purpose                             |
|------------------------|-------------------------------------|
| `/products-by-category` | Fetch product listings by category |
| `/product-reviews`      | (Optional) Fetch product reviews   |
| `/product-details`      | (Optional) Fetch product details   |

> 🔐 Requires `x-rapidapi-key` authentication.  
> ⚠️ Free tier supports **100 requests/month**, so the script includes delays and pagination limits.

---

## 📜 Python Script Features

**File**: `Fetch_Clean_Mysql_schedule.py`

- Fetches data from multiple Amazon categories (up to 5 pages/category)
- Cleans fields (e.g., price → float, sales volume → numeric)
- Computes:
  - `quantity` (random logic based on price range)
  - `total_sales` = `price × quantity`
- Adds simulated `location` for map insights
- Saves cleaned data to MySQL
- Runs every 6 hours via scheduler

---

## 🗃️ Database Schema

**Table**: `amazon_products`

| Column         | Type     | Description                          |
|----------------|----------|--------------------------------------|
| `product_id`   | TEXT     | Amazon ASIN                          |
| `title`        | TEXT     | Product title                        |
| `category`     | TEXT     | Product category                     |
| `price`        | FLOAT    | Product price                        |
| `quantity`     | INT      | Simulated quantity sold              |
| `total_sales`  | FLOAT    | price × quantity                     |
| `currency`     | TEXT     | Usually "USD"                        |
| `rating`       | FLOAT    | Star rating                          |
| `total_reviews`| INT      | Number of reviews                    |
| `sales_volume` | INT      | Estimated purchase volume            |
| `is_prime`     | BOOLEAN  | Prime-eligible                       |
| `delivery`     | TEXT     | Delivery info                        |
| `location`     | TEXT     | Simulated US city for mapping        |
| `url`          | TEXT     | Product URL                          |

---

## 📊 Tableau Dashboard

**File**: `Amazon_sales_dashboard_tableau.twb`

### 📈 Key Insights

| Sheet Name             | Visualization     | Insight                                     |
|------------------------|-------------------|---------------------------------------------|
| Sales by Category      | Bar Chart         | Total sales by product category             |
| Sales by City (Map)    | Filled Map        | Geographic distribution of sales            |
| Top 10 Products Sold   | Bar Chart         | Highest total sales products                |
| Top 10 Rated Products  | Bar Chart         | Highest rated products                      |
| KPI Boxes              | Numeric Boxes     | Total Sales, Avg Price, Avg Rating, Count   |
| Interactive Filters    | Filter Panel      | Category, City, Price range, Prime status   |

✅ Includes full dashboard interactivity: selecting a city filters all visuals, category filter syncs across charts, and a price range slider lets users explore product segments.

---
> ![image](https://github.com/user-attachments/assets/891aaab4-bea0-4a47-84e9-78fd482b95eb)

## 🧠 Future Improvements

- 🔍 Add product sentiment analysis from reviews
- 🖼️ Embed product images into dashboard
- 🔄 Connect Tableau live to MySQL for real-time refresh
- ☁️ Push backups to AWS S3 or Google Cloud
- 📊 Add trend analysis (requires date simulation or real-time logging)
- ⏱️ Replace `schedule` with Airflow for enterprise task orchestration

---

## 📁 Repository Structure

```bash
.
├── Fetch_Clean_Mysql_schedule.py     # Main ETL + scheduler script
├── .env                              # API key & DB credentials (not committed)
├── Amazon_sales_dashboard_tableau.twb # Tableau Dashboard
├── final_amazon_dashboard_data.csv   # Cleaned data sample
├── README.md                         # Project documentation

## 📌 Author

**Amogh Shrinivas Goudar**  
_Data Analyst | Python | SQL | Power BI_  
[LinkedIn](https://www.linkedin.com) | [Portfolio](https://yourportfolio.com) *(Add yours)*

---

## 📁 License

MIT License — feel free to use or extend!
