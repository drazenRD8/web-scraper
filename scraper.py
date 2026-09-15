import requests
import json
import csv
import time
import random
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin

# Lista modernih browsera kako nas sajt ne bi detektovao kao bota odmah
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]


def scrape_quotes(base_url, pages, output_file, format_type):
    current_url = base_url
    all_data = []
    page_count = 0
    MAX_PAGES = 50

    if pages > MAX_PAGES:
        pages = MAX_PAGES

    print(f"[*] Započinjem skrejpovanje (maksimalno {pages} stranica)...")

    while current_url and page_count < pages:
        # 1. Rotacija User-Agenta za svaki zahtev
        headers = {"User-Agent": random.choice(USER_AGENTS)}

        try:
            print(f"[*] Skrejpujem stranicu: {current_url}")
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[-] Greška u mreži: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        # 2. Defanzivna obrada podataka (Zaštita od izmena u HTML-u sajta)
        for q in quotes:
            text_el = q.find("span", class_="text")
            author_el = q.find("small", class_="author")

            text = text_el.get_text(strip=True) if text_el else "Nema teksta"
            author = author_el.get_text(strip=True) if author_el else "Nepoznat autor"
            all_data.append({"text": text, "author": author})

        page_count += 1

        next_btn = soup.find("li", class_="next")
        if next_btn and next_btn.find("a"):
            next_page_relative = next_btn.find("a")["href"]
            current_url = urljoin(base_url, next_page_relative)

            # 3. Simulacija ljudskog ponašanja - nasumična pauza od 1.5 do 3 sekunde
            sleep_time = random.uniform(1.5, 3.0)
            print(f"[i] Pravim pauzu od {sleep_time:.2f}s radi simulacije ljudskog ponašanja...")
            time.sleep(sleep_time)
        else:
            current_url = None

    if not all_data:
        print("[-] Nema pronađenih podataka.")
        return

    path = Path(output_file)
    counter = 1
    while path.exists():
        path = Path(f"{path.stem}_{counter}{path.suffix}")
        counter += 1

    if format_type == "json":
        path.write_text(json.dumps(all_data, indent=2, ensure_ascii=False), encoding="utf-8")
    elif format_type == "csv":
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "author"])
            writer.writeheader()
            writer.writerows(all_data)

    print(f"[+] Uspješno sačuvano {len(all_data)} citata u '{path}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Napredni skreper citata sa paginacijom")
    parser.add_argument("--url", default="http://quotes.toscrape.com/", help="Početni URL")
    parser.add_argument("--pages", type=int, default=3, help="Broj stranica")
    parser.add_argument("--output", default="quotes", help="Naziv fajla")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Format")
    args = parser.parse_args()

    output_filename = f"{args.output}.{args.format}"
    scrape_quotes(args.url, args.pages, output_filename, args.format)