CREATE DATABASE amazon_dashboard;
USE amazon_dashboard ;
CREATE TABLE amazon_products (
    product_id VARCHAR(20) PRIMARY KEY,
    title TEXT,
    category VARCHAR(100),
    price DECIMAL(10, 2),
    currency VARCHAR(10),
    quantity INT,
    total_sales DECIMAL(12, 2),
    rating DECIMAL(3, 2),
    total_reviews INT,
    is_prime BOOLEAN,
    sales_volume INT,
    delivery TEXT,
    location VARCHAR(100),
    url TEXT
);
