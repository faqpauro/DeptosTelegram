import logging
import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from config import MAX_PRICE, is_location_valid
from scrapers.browser_fetch import fetch_html_with_playwright

logger = logging.getLogger(__name__)

SEARCH_URLS = [
    ("Villa Devoto", f"https://www.argenprop.com/departamento-alquiler-barrio-villa-devoto-hasta-{MAX_PRICE}-pesos"),
    ("Villa Real", f"https://www.argenprop.com/departamento-alquiler-barrio-villa-real-hasta-{MAX_PRICE}-pesos")
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

def fetch_argenprop():
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
                    logger.info(f"[Argenprop] Status code {r.status_code}. Intentando con Playwright Chromium...")
                    html = fetch_html_with_playwright(url)
            except Exception:
                logger.info("[Argenprop] Fallo HTTP directo. Intentando con Playwright Chromium...")
                html = fetch_html_with_playwright(url)

            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.select('.listing__item')
            logger.info(f"[Argenprop] Encontradas {len(cards)} publicaciones en {neighborhood}")

            for card in cards:
                try:
                    link_el = card.select_one('a.card')
                    if not link_el or 'href' not in link_el.attrs:
                        continue
                    
                    rel_link = link_el['href']
                    full_link = "https://www.argenprop.com" + rel_link if not rel_link.startswith("http") else rel_link
                    
                    prop_id_match = re.search(r'--(\d+)', rel_link)
                    prop_id = f"argenprop_{prop_id_match.group(1)}" if prop_id_match else f"argenprop_{hash(full_link)}"

                    title_el = card.select_one('.card__title') or card.select_one('.card__address')
                    title = title_el.get_text(strip=True) if title_el else f"Departamento en Alquiler en {neighborhood}"

                    address_el = card.select_one('.card__address')
                    address = address_el.get_text(strip=True) if address_el else neighborhood

                    # FILTRO DE UBICACIÓN ESTRICTO
                    if not is_location_valid(address, title, neighborhood):
                        logger.debug(f"[Argenprop] Ignorando propiedad fuera del barrio deseado: {address} | {title}")
                        continue

                    price_el = card.select_one('.card__price')
                    raw_price_text = price_el.get_text(" ", strip=True) if price_el else ""
                    
                    if "USD" in raw_price_text.upper():
                        continue

                    num_price = parse_price(raw_price_text)
                    if num_price > MAX_PRICE or num_price <= 0:
                        continue

                    expensas_match = re.search(r'\+\s*\$\s*([\d\.]+)\s*expensas', raw_price_text, re.IGNORECASE)
                    expensas_text = f"+ ${expensas_match.group(1)} exp" if expensas_match else "Sin expensas acl."

                    properties.append({
                        "id": prop_id,
                        "source": "Argenprop",
                        "title": title,
                        "address": address,
                        "location": neighborhood,
                        "price": f"${num_price:,}".replace(",", "."),
                        "price_num": num_price,
                        "expensas": expensas_text,
                        "url": full_link
                    })
                except Exception as card_err:
                    logger.debug(f"[Argenprop] Error parseando tarjeta: {card_err}")
                    continue

        except Exception as e:
            logger.error(f"[Argenprop] Error en scraping de {neighborhood}: {e}")

    return properties
