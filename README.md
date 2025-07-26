# 🛒 South African Grocery Price Tracker

A lightweight scraper and tracker for South African grocery store products. This project currently extracts product details from **Pick n Pay** and stores the data as JSON files, versioned by date. Weekly automated scrapes are performed via GitHub Actions.

https://heelinmistry.github.io/grocery_price_tracker/

## 📦 Features

- Extracts product data (name, price, discount, promo) from Pick n Pay
- Weekly auto-update using GitHub Actions
- JSON files saved using `YYYY-MM-DD` format
- Supports GitHub Pages interface (filter, search, explore)

## 🧰 Technologies Used

- Python (`pandas`, `requests`, `beautifulsoup4` or `playwright`)
- GitHub Actions (CI for weekly scrapes)
- JSON output for frontend/web use
- Optional GitHub Pages frontend (filtering/search)

---

## 🚀 Getting Started

### 1. Clone the Repository

git clone https://github.com/HeelinMistry/grocery_price_tracker.git

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Run Locally

python main.py          
