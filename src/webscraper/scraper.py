import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

URL = "https://books.toscrape.com/"
response = requests.get(URL)

soup = BeautifulSoup(response.text, "html.parser")

# Extract book titles and prices
books = soup.find_all("article", class_="product_pod")

data = []
for book in books:
    title = book.h3.a["title"]
    price = book.find("p", class_="price_color").text
    data.append({"title": title, "price": price})

# Convert to DataFrame
df = pd.DataFrame(data)
print(df)

# Save to CSV (optional) — ensure the data directory exists and write there
out_dir = Path(__file__).resolve().parents[2] / "data"
out_dir.mkdir(parents=True, exist_ok=True)
csv_path = out_dir / "books.csv"
df.to_csv(csv_path, index=False)
print(f"Scraped data saved to {csv_path}")
