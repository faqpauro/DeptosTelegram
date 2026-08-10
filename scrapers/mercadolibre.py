import logging
import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from config import MAX_PRICE, is_location_valid
from scrapers.browser_fetch import fetch_html_with_playwright

logger = logging.getLogger(__name__)

SEARCH_URLS = [
    ("Villa Devoto", "https://listado.mercadolibre.com.ar/alquiler-departamento-villa-devoto"),
    ("Villa Real", "https://listado.mercadolibre.com.ar/alquiler-departamento-villa-real")
]

def parse_price(price_text: str) -> int:
    if not price_text:
        return 0
    clean = re.sub(r'[^\d]', '', price_text)
    try:
        return int(clean)
    except ValueError:
        return 0

def fetch_mercadolibre():
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
                if r.status_code == 200 and "ui-search" in r.text:
                    html = r.text
                else:
                    logger.info(f"[MercadoLibre] Usando Playwright Chromium para {url}...")
                    html = fetch_html_with_playwright(url)
            except Exception:
                logger.info(f"[MercadoLibre] Usando Playwright Chromium para {url}...")
                html = fetch_html_with_playwright(url)

            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            cards = (
                soup.select('li.ui-search-layout__item') or
                soup.select('.poly-card') or
                soup.select('.ui-search-result__wrapper')
            )

            logger.info(f"[MercadoLibre] Encontradas {len(cards)} publicaciones en {neighborhood}")

            for card in cards:
                try:
                    link_el = (
                        card.select_one('a.ui-search-link') or
                        card.select_one('a.poly-component__title') or
                        card.select_one('a')
                    )
                    if not link_el or 'href' not in link_el.attrs:
                        continue

                    full_link = link_el['href']

                    prop_id_match = re.search(r'MLA-?(\d+)', full_link)
                    prop_id = f"ml_{prop_id_match.group(1)}" if prop_id_match else f"ml_{hash(full_link)}"

                    title_el = (
                        card.select_one('.ui-search-item__title') or
                        card.select_one('.poly-component__title') or
                        card.select_one('h2')
                    )
                    title = title_el.get_text(strip=True) if title_el else f"Departamento en Alquiler en {neighborhood}"

                    location_el = card.select_one('.ui-search-item__location') or card.select_one('.poly-component__location')
                    address = location_el.get_text(strip=True) if location_el else neighborhood

                    # FILTRO DE UBICACIÓN ESTRICTO
                    if not is_location_valid(address, title, neighborhood):
                        continue

                    price_fraction = (
                        card.select_one('.andes-money-amount__fraction') or
                        card.select_one('.poly-price__current .andes-money-amount__fraction')
                    )
                    raw_price = price_fraction.get_text(strip=True) if price_fraction else ""

                    symbol_el = card.select_one('.andes-money-amount__currency-symbol')
                    symbol = symbol_el.get_text(strip=True) if symbol_el else "$"

                    if "U$S" in symbol or "USD" in symbol:
                        continue

                    num_price = parse_price(raw_price)
                    if num_price > MAX_PRICE or num_price <= 0:
                        continue

                    properties.append({
                        "id": prop_id,
                        "source": "MercadoLibre",
                        "title": title,
                        "address": address,
                        "location": neighborhood,
                        "price": f"${num_price:,}".replace(",", "."),
                        "price_num": num_price,
                        "expensas": "Ver en publicación",
                        "url": full_link
                    })
                except Exception as card_err:
                    logger.debug(f"[MercadoLibre] Error parseando tarjeta: {card_err}")
                    continue

        except Exception as e:
            logger.error(f"[MercadoLibre] Error en scraping de {neighborhood}: {e}")

    return properties
