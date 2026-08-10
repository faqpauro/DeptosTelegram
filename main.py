import sys
import os
import time
import logging
import argparse

# Configurar encoding utf-8 para la consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MAX_PRICE, LOCATIONS, CHECK_INTERVAL_MINUTES
from database import init_db, is_property_seen, mark_property_as_seen
from scrapers.argenprop import fetch_argenprop
from scrapers.zonaprop import fetch_zonaprop
from scrapers.mercadolibre import fetch_mercadolibre
from telegram_notifier import send_telegram_message, format_property_message

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DeptosBot")

def run_scan():
    """Ejecuta el escaneo completo en todos los portales y notifica novedades."""
    logger.info("==================================================")
    logger.info(f"[*] Iniciando escaneo de departamentos en {', '.join(LOCATIONS)}")
    logger.info(f"[*] Filtro precio maximo: ${MAX_PRICE:,}".replace(",", "."))
    logger.info("==================================================")

    all_properties = []

    # 1. Argenprop
    logger.info("[+] Escaneando Argenprop...")
    argenprop_items = fetch_argenprop()
    all_properties.extend(argenprop_items)

    # 2. Zonaprop
    logger.info("[+] Escaneando Zonaprop...")
    zonaprop_items = fetch_zonaprop()
    all_properties.extend(zonaprop_items)

    # 3. Mercado Libre
    logger.info("[+] Escaneando Mercado Libre...")
    ml_items = fetch_mercadolibre()
    all_properties.extend(ml_items)

    logger.info(f"[=] Total publicaciones recolectadas de portales: {len(all_properties)}")

    new_count = 0
    for prop in all_properties:
        prop_id = prop["id"]

        # Verificar si ya la enviamos antes
        if is_property_seen(prop_id):
            continue

        # ¡Es un nuevo departamento!
        logger.info(f"[!] NUEVO DEPARTAMENTO: [{prop['source']}] {prop['title']} - {prop['price']} ({prop['location']})")
        
        # Formatear y enviar mensaje a Telegram
        msg_html = format_property_message(prop)
        success = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg_html)

        # Guardar en base de datos para no repetirlo
        mark_property_as_seen(
            prop_id=prop_id,
            source=prop["source"],
            title=prop["title"],
            price=prop["price"],
            location=prop["location"],
            url=prop["url"]
        )
        new_count += 1
        time.sleep(0.5)

    logger.info(f"[V] Escaneo completado. Departamentos nuevos notificados: {new_count}")

def main():
    parser = argparse.ArgumentParser(description="Bot Alertas Alquileres Telegram")
    parser.add_argument("--once", action="store_true", help="Ejecuta un solo escaneo y termina")
    parser.add_argument("--test-telegram", action="store_true", help="Envía un mensaje de prueba a Telegram")
    args = parser.parse_args()

    # Inicializar Base de Datos
    init_db()

    if args.test_telegram:
        print("[*] Enviando mensaje de prueba a Telegram...")
        test_msg = (
            "<b>🤖 ¡Bot de Alertas de Alquileres Activado!</b>\n\n"
            "📍 <b>Filtros:</b> Villa Devoto y Villa Real\n"
            "💵 <b>Precio Máx:</b> $950.000 (sin expensas)\n"
            "🏢 <b>Portales:</b> Argenprop, Zonaprop, Mercado Libre\n\n"
            "Recibirás un mensaje automático apenas aparezcan nuevos departamentos."
        )
        ok = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, test_msg)
        if ok:
            print("[V] Mensaje de prueba enviado con éxito a Telegram!")
        else:
            print("[X] No se pudo enviar el mensaje. Revisa TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en config.py")
        return

    # Escaneo inicial
    run_scan()

    if args.once:
        return

    logger.info(f"[*] Bucle activo. Siguiente escaneo en {CHECK_INTERVAL_MINUTES} minutos...")
    try:
        while True:
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
            run_scan()
    except KeyboardInterrupt:
        logger.info("[*] Bot detenido manualmente.")

if __name__ == "__main__":
    main()
