import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from time import sleep
import sys

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

all_data = []

for page in range(1, 51):
    url = BASE_URL.format(page)
    print(f"Scraping Page {page}...", file=sys.stderr, flush=True)

    try:
        response = requests.get(url, timeout=10)  # ⬅ timeout prevents hanging
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print(f" Timeout on page {page}, retrying...", file=sys.stderr, flush=True)
        sleep(2)
        continue

    except requests.exceptions.RequestException as e:
        print(f" Failed to load page {page}: {e}", file=sys.stderr, flush=True)
        break

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    if not books:
        print(f" No books found on page {page}, stopping.", file=sys.stderr, flush=True)
        break

    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()
        # Clean up encoding artifacts
        price = price.replace("\xa0", "").replace("\u00a0", "").strip()
        all_data.append({"title": title, "price": price})

    print(f"  ✓ Scraped {len(books)} books from page {page}", file=sys.stderr, flush=True)
    sleep(1)  # polite delay so we don't hammer the site

# Store results
df = pd.DataFrame(all_data)
print(f"\n✔ Total scraped: {len(df)} books", file=sys.stderr, flush=True)

out_dir = PROJECT_ROOT / "data"
out_dir.mkdir(exist_ok=True)
csv_path = out_dir / "books.csv"

file_exists = csv_path.exists()
df.to_csv(csv_path, mode='w', index=False, encoding='utf-8')

print(f"✔ Saved {len(df)} rows to {csv_path}", file=sys.stderr, flush=True)
