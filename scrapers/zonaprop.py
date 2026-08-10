import logging
import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from config import MAX_PRICE
from scrapers.browser_fetch import fetch_html_with_playwright

logger = logging.getLogger(__name__)

SEARCH_URLS = [
    ("Villa Devoto", f"https://www.zonaprop.com.ar/departamentos-alquiler-villa-devoto-hasta-{MAX_PRICE}-pesos.html"),
    ("Villa Real", f"https://www.zonaprop.com.ar/departamentos-alquiler-villa-real-hasta-{MAX_PRICE}-pesos.html")
]

def parse_price(price_text: str) -> int:
    if not price_text:
        return 0
    match = re.search(r'\$\s*([\d\.]+)', price_text)
    if match:
        clean_str = match.group(1).replace('.', '')
        try:
            return int(clean_str)
        except ValueError:
            return 0
    return 0

def fetch_zonaprop():
    properties = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    for neighborhood, url in SEARCH_URLS:
        try:
            html = ""
            try:
                r = requests.get(url, impersonate="chrome120", headers=headers, timeout=15)
                if r.status_code == 200:
                    html = r.text
                else:
                    logger.info(f"[Zonaprop] Status code {r.status_code}. Intentando con Playwright Chromium...")
                    html = fetch_html_with_playwright(url)
            except Exception:
                logger.info("[Zonaprop] Fallo HTTP directo. Intentando con Playwright Chromium...")
                html = fetch_html_with_playwright(url)

            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.select('.postingCard') or soup.select('[data-id]') or soup.select('div[class*="PostingCard"]')
            logger.info(f"[Zonaprop] Encontradas {len(cards)} publicaciones en {neighborhood}")

            for card in cards:
                try:
                    link_el = card.select_one('a.go-to-posting') or card.select_one('a[href*="/propiedades/"]') or card.select_one('a')
                    if not link_el or 'href' not in link_el.attrs:
                        continue
                    
                    rel_link = link_el['href']
                    full_link = "https://www.zonaprop.com.ar" + rel_link if not rel_link.startswith("http") else rel_link

                    prop_id_match = re.search(r'-(\d+)\.html', rel_link)
                    prop_id = f"zonaprop_{prop_id_match.group(1)}" if prop_id_match else f"zonaprop_{hash(full_link)}"

                    title_el = card.select_one('.postingCardTitle') or card.select_one('h2') or card.select_one('[class*="Title"]')
                    title = title_el.get_text(strip=True) if title_el else f"Departamento en Alquiler en {neighborhood}"

                    location_el = card.select_one('.postingCardLocation') or card.select_one('[class*="Location"]') or card.select_one('[class*="Address"]')
                    address = location_el.get_text(strip=True) if location_el else neighborhood

                    price_el = card.select_one('.firstPrice') or card.select_one('.postingCardPrice') or card.select_one('[class*="Price"]')
                    raw_price_text = price_el.get_text(" ", strip=True) if price_el else ""

                    if "USD" in raw_price_text.upper() or "U$S" in raw_price_text.upper():
                        continue

                    num_price = parse_price(raw_price_text)
                    if num_price > MAX_PRICE or num_price <= 0:
                        continue

                    expensas_el = card.select_one('.expenses') or card.select_one('[class*="Expenses"]')
                    expensas_text = expensas_el.get_text(strip=True) if expensas_el else "Sin expensas acl."

                    properties.append({
                        "id": prop_id,
                        "source": "Zonaprop",
                        "title": title,
                        "address": address,
                        "location": neighborhood,
                        "price": f"${num_price:,}".replace(",", "."),
                        "price_num": num_price,
                        "expensas": expensas_text,
                        "url": full_link
                    })
                except Exception as card_err:
                    logger.debug(f"[Zonaprop] Error parseando tarjeta: {card_err}")
                    continue

        except Exception as e:
            logger.error(f"[Zonaprop] Error en scraping de {neighborhood}: {e}")

    return properties
