import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def fetch_html_with_playwright(url: str, timeout: int = 30000) -> str:
    """Descarga el HTML cargado completamente usando Playwright Chromium con bypass stealth."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="es-AR",
                timezone_id="America/Argentina/Buenos_Aires",
                viewport={"width": 1366, "height": 768}
            )
            page = context.new_page()
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['es-AR', 'es']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            """)
            
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            page.wait_for_timeout(4000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        logger.error(f"[Playwright] Error al obtener {url}: {e}")
        return ""
