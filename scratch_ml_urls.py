import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from curl_cffi import requests
from bs4 import BeautifulSoup

urls = [
    "https://inmuebles.mercadolibre.com.ar/alquiler/departamentos/villa-devoto/",
    "https://inmuebles.mercadolibre.com.ar/alquiler/departamentos/villa-real/",
    "https://listado.mercadolibre.com.ar/alquiler-departamento-villa-devoto",
    "https://listado.mercadolibre.com.ar/alquiler-departamento-villa-real"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

for url in urls:
    r = requests.get(url, impersonate="chrome120", headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.select('.ui-search-layout__item') or soup.select('.poly-card') or soup.select('li.ui-search-layout__item') or soup.select('.ui-search-result__wrapper')
    print(f"URL: {url} -> Status: {r.status_code} | Items: {len(items)}")
    if items:
        for it in items[:2]:
            t = it.select_one('.ui-search-item__title') or it.select_one('.poly-component__title') or it.select_one('h2')
            p = it.select_one('.andes-money-amount__fraction')
            print(f"   Item: {t.get_text(strip=True) if t else 'N/A'} | Price: ${p.get_text(strip=True) if p else 'N/A'}")
