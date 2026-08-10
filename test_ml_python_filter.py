import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from scrapers.browser_fetch import fetch_html_with_playwright
from bs4 import BeautifulSoup
from config import MAX_PRICE, is_location_valid
import re

urls = [
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

for neighborhood, url in urls:
    print(f"Fetching ML for {neighborhood}: {url}")
    html = fetch_html_with_playwright(url)
    soup = BeautifulSoup(html, 'html.parser')
    
    cards = (
        soup.select('li.ui-search-layout__item') or
        soup.select('.poly-card') or
        soup.select('.ui-search-result__wrapper')
    )
    print(f"  Found {len(cards)} raw cards for {neighborhood}")
    
    valid_count = 0
    for c in cards:
        title_el = c.select_one('.ui-search-item__title') or c.select_one('.poly-component__title') or c.select_one('h2')
        price_el = c.select_one('.andes-money-amount__fraction') or c.select_one('.poly-price__current .andes-money-amount__fraction')
        location_el = c.select_one('.ui-search-item__location') or c.select_one('.poly-component__location')
        link_el = c.select_one('a')
        
        title = title_el.get_text(strip=True) if title_el else ""
        price_str = price_el.get_text(strip=True) if price_el else ""
        location = location_el.get_text(strip=True) if location_el else neighborhood
        link = link_el['href'] if link_el and 'href' in link_el.attrs else ""
        
        num_price = parse_price(price_str)
        if num_price > MAX_PRICE or num_price <= 0:
            continue
            
        if not is_location_valid(location, title, neighborhood):
            continue
            
        valid_count += 1
        print(f"   * [ML {neighborhood}] {title} - ${num_price:,}".replace(",", ".") + f" | {link[:60]}...")
            
    print(f"  Valid matching properties <= $950.000 for {neighborhood}: {valid_count}\n")
