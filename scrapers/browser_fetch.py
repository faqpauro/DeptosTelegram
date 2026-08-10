import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def fetch_html_with_playwright(url: str, timeout: int = 30000) -> str:
    """Descarga el HTML cargado completamente usando Playwright Chromium para evadir Cloudflare/403."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="es-AR",
                timezone_id="America/Argentina/Buenos_Aires"
            )
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            page.wait_for_timeout(3000)  # Esperar renderizado JS / bypass Cloudflare
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        logger.error(f"[Playwright] Error al obtener {url}: {e}")
        return ""
