import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://listado.mercadolibre.com.ar/alquiler-departamentos-villa-devoto"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(3000)
    print("Page title:", page.title())
    cards = page.query_selector_all('li.ui-search-layout__item, .poly-card, .ui-search-result__wrapper')
    print("PW items count:", len(cards))
    for c in cards[:3]:
        t = c.query_selector('.ui-search-item__title, .poly-component__title, h2')
        p_el = c.query_selector('.andes-money-amount__fraction')
        print(f"  * {t.inner_text() if t else 'N/A'} | ${p_el.inner_text() if p_el else 'N/A'}")
    browser.close()
