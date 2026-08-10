import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from scrapers.browser_fetch import fetch_html_with_playwright
from bs4 import BeautifulSoup

url = "https://inmuebles.mercadolibre.com.ar/alquiler/departamentos/capital-federal/villa-devoto/"
print("Fetching ML with Playwright:", url)
html = fetch_html_with_playwright(url)
soup = BeautifulSoup(html, 'html.parser')
items = soup.select('.ui-search-layout__item') or soup.select('.poly-card') or soup.select('ol li.ui-search-layout__item')
print(f"Playwright items found: {len(items)}")

for it in items[:3]:
    t = it.select_one('.ui-search-item__title') or it.select_one('.poly-component__title') or it.select_one('h2')
    p = it.select_one('.andes-money-amount__fraction')
    l = it.select_one('a')
    print(f"  * {t.get_text(strip=True) if t else 'N/A'} | ${p.get_text(strip=True) if p else 'N/A'} | {l['href'] if l else 'N/A'}")
