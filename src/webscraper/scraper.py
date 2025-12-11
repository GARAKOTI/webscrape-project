import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from time import sleep
import sys
import logging
from logging.handlers import RotatingFileHandler

# -------------------------------
# LOGGING SETUP
# -------------------------------

# Project root (two levels above this script)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Create logs directory
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logger
logger = logging.getLogger("book_scraper")
logger.setLevel(logging.INFO)

# Rotate log file at 1MB, keep 3 backups
log_file = LOG_DIR / "scraper.log"
handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)

# Log format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# -------------------------------
# SCRAPER
# -------------------------------

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

all_data = []

for page in range(1, 51):

    url = BASE_URL.format(page)
    logger.info(f"Scraping Page {page} — {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout on page {page}, retrying...")
        sleep(2)
        continue

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to load page {page}: {e}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    if not books:
        logger.warning(f"No books found on page {page}. Stopping scraper.")
        break

    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()

        price = price.replace("\xa0", "").replace("\u00a0", "").strip()

        all_data.append({"title": title, "price": price})

    logger.info(f"✓ Scraped {len(books)} books from page {page}")
    sleep(1)  # polite delay

# -------------------------------
# SAVE RESULTS
# -------------------------------

df = pd.DataFrame(all_data)
logger.info(f"Total scraped: {len(df)} books")

out_dir = PROJECT_ROOT / "data"
out_dir.mkdir(exist_ok=True)
csv_path = out_dir / "books.csv"

df.to_csv(csv_path, mode="w", index=False, encoding="utf-8")
logger.info(f"Saved {len(df)} rows to {csv_path}")
