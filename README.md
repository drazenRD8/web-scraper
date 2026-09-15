# Web Scraper

Mali Python alat za skrejpovanje citata sa sajta quotes.toscrape.com, sa podrškom za paginaciju i čuvanje u JSON ili CSV.

**Verzija:** v2.0.0

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
[i] Pravim pauzu od 2.15s radi simulacije ljudskog ponašanja...
[*] Skrejpujem stranicu: http://quotes.toscrape.com/page/2/
[i] Pravim pauzu od 1.87s radi simulacije ljudskog ponašanja...
[*] Skrejpujem stranicu: http://quotes.toscrape.com/page/3/
[+] Uspješno sačuvano 30 citata u 'quotes.json'.

## Funkcije

- **Rotacija User-Agenta**: Simulira različite browsere (Chrome, Firefox, Safari).
- **Nasumične pauze**: 1.5-3 sekunde između zahteva (simulira ljudsko ponašanje).
- **Defanzivna obrada**: Proverava da li element postoji pre nego što ga čita.
- **Paginacija**: Automatski prelazi na sledeću stranicu.
- **JSON/CSV izlaz**: Strukturirani podaci.
- **Limit stranica**: Maksimalno 50 stranica.

## Napomena

Ovaj alat je napravljen za edukaciju i OSINT vežbe.