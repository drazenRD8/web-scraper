# web-scraper
Simple web scraper with pagination support, saves quotes to JSON or CSV
# Web Scraper

Mali Python alat za skrejpovanje citata sa sajta quotes.toscrape.com, sa podrškom za paginaciju i čuvanje u JSON ili CSV.

## Instalacija

pip install -r requirements.txt

## Pokretanje

python scraper.py

## CLI upotreba

# Skrejpuj 3 stranice i sačuvaj u JSON
python scraper.py --pages 3 --format json

# Skrejpuj 5 stranica i sačuvaj u CSV
python scraper.py --pages 5 --format csv

# Promeni izlazni fajl
python scraper.py --output moji_citati --pages 2

## Primer

[*] Započinjem skrejpovanje (maksimalno 3 stranica)...
[*] Skrejpujem stranicu: http://quotes.toscrape.com/
[*] Skrejpujem stranicu: http://quotes.toscrape.com/page/2/
[*] Skrejpujem stranicu: http://quotes.toscrape.com/page/3/
[+] Uspješno sačuvano 30 citata u 'quotes.json' (JSON).

## Napomena

Ovaj alat je napravljen za edukaciju i OSINT vežbe.
