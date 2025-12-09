import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

URL = "https://books.toscrape.com/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

books = soup.find_all("article", class_="product_pod")

data = []
for book in books:
    title = book.h3.a["title"]
    price = book.find("p", class_="price_color").text
    data.append({"title": title, "price": price})

df = pd.DataFrame(data)
print(df)

# ---- FIXED PATH ----
out_dir = Path("data")
out_dir.mkdir(exist_ok=True)

csv_path = out_dir / "books.csv"

# ---- CHECK BEFORE WRITE ----
file_exists = csv_path.exists()

# ---- APPEND MODE ----
df.to_csv(csv_path, mode="a", index=False, header=not file_exists)

print(f"✔ Data appended to {csv_path}")
