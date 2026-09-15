import requests
import json
import csv
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin


def scrape_quotes(base_url, pages, output_file, format_type):
    """Skrejpuje citate sa više stranica i čuva ih u JSON ili CSV fajl."""
    headers = {"User-Agent": "Mozilla/5.0"}
    current_url = base_url
    all_data = []
    page_count = 0
    MAX_PAGES = 50  # Zaštita od prevelikog broja stranica

    if pages > MAX_PAGES:
        print(f"[!] Maksimalan broj stranica je {MAX_PAGES}. Postavljam na {MAX_PAGES}.")
        pages = MAX_PAGES

    print(f"[*] Započinjem skrejpovanje (maksimalno {pages} stranica)...")

    while current_url and page_count < pages:
        try:
            print(f"[*] Skrejpujem stranicu: {current_url}")
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[-] Greška u mreži: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        for q in quotes:
            text = q.find("span", class_="text").get_text(strip=True)
            author = q.find("small", class_="author").get_text(strip=True)
            all_data.append({"text": text, "author": author})

        page_count += 1

        next_btn = soup.find("li", class_="next")
        if next_btn and next_btn.find("a"):
            next_page_relative = next_btn.find("a")["href"]
            current_url = urljoin(base_url, next_page_relative)
        else:
            current_url = None

    if not all_data:
        print("[-] Nema pronađenih podataka.")
        return

    path = Path(output_file)
    # Zaštita: ako fajl već postoji, dodaj broj
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

    print(f"[+] Uspješno sačuvano {len(all_data)} citata u '{path}' ({format_type.upper()}).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Napredni skreper citata sa paginacijom")
    parser.add_argument("--url", default="http://quotes.toscrape.com/", help="Početni URL")
    parser.add_argument("--pages", type=int, default=3, help="Broj stranica za skrejpovanje")
    parser.add_argument("--output", default="quotes", help="Naziv izlaznog fajla (bez ekstenzije)")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Izlazni format fajla")
    args = parser.parse_args()

    output_filename = f"{args.output}.{args.format}"
    scrape_quotes(args.url, args.pages, output_filename, args.format)