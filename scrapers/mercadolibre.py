import logging
import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from config import MAX_PRICE, is_location_valid
from scrapers.browser_fetch import fetch_html_with_playwright

logger = logging.getLogger(__name__)

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
    seen_ids = set()

    search_urls = [
        # 1. URL exacta con filtro Publicados Hoy y NoIndex en Villa Devoto y Villa Real
        ("Villa Devoto / Villa Real (Hoy)", f"https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/capital-federal/villa-real-o-villa-devoto/_PriceRange_0ARS-{MAX_PRICE}ARS_PublishedToday_YES_NoIndex_True"),
        # 2. URL general con filtro de precio en Villa Devoto y Villa Real
        ("Villa Devoto / Villa Real (Todos)", f"https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/capital-federal/villa-real-o-villa-devoto/_PriceRange_0ARS-{MAX_PRICE}ARS"),
        # 3. URL alternativa por barrio
        ("Villa Devoto", f"https://listado.mercadolibre.com.ar/alquiler-departamentos-villa-devoto_Hasta_{MAX_PRICE}"),
        ("Villa Real", f"https://listado.mercadolibre.com.ar/alquiler-departamentos-villa-real_Hasta_{MAX_PRICE}")
    ]

    # Usar User-Agent de Googlebot para evitar el bloqueo 'account-verification' / 'suspicious-traffic' de MercadoLibre
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    for label, url in search_urls:
        try:
            html = ""
            try:
                r = requests.get(url, impersonate="chrome120", headers=headers, timeout=15)
                if r.status_code == 200 and ("ui-search" in r.text or "poly-card" in r.text):
                    html = r.text
                else:
                    logger.info(f"[MercadoLibre] Fallback curl_cffi para {label}, usando Playwright...")
                    html = fetch_html_with_playwright(url)
            except Exception as req_err:
                logger.info(f"[MercadoLibre] Error en request ({req_err}), usando Playwright para {label}...")
                html = fetch_html_with_playwright(url)

            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            cards = (
                soup.select('li.ui-search-layout__item') or
                soup.select('.poly-card') or
                soup.select('.ui-search-result__wrapper')
            )

            logger.info(f"[MercadoLibre] Encontradas {len(cards)} publicaciones en {label}")

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

                    if prop_id in seen_ids:
                        continue

                    title_el = (
                        card.select_one('.ui-search-item__title') or
                        card.select_one('.poly-component__title') or
                        card.select_one('h2')
                    )
                    title = title_el.get_text(strip=True) if title_el else "Departamento en Alquiler"

                    location_el = card.select_one('.ui-search-item__location') or card.select_one('.poly-component__location')
                    address = location_el.get_text(strip=True) if location_el else label

                    # Determinar barrio
                    neighborhood = "Villa Devoto"
                    if "villa real" in address.lower() or "villa real" in title.lower():
                        neighborhood = "Villa Real"

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

                    seen_ids.add(prop_id)
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
            logger.error(f"[MercadoLibre] Error en scraping de {label}: {e}")

    return properties
