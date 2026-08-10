import logging
import requests

logger = logging.getLogger(__name__)

def send_telegram_message(bot_token: str, chat_id_str: str, message_html: str) -> bool:
    """Envía un mensaje formateado con HTML a uno o múltiples chat_ids de Telegram separados por coma."""
    if not bot_token or not chat_id_str:
        logger.warning("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no estan configurados")
        print("[!] ALERTA: No has configurado TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID aun.")
        return False

    # Soportar múltiples IDs separados por coma (ej: "6608835035,9876543210")
    chat_ids = [c.strip() for c in chat_id_str.split(",") if c.strip()]
    overall_success = True

    for cid in chat_ids:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": cid,
            "text": message_html,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Mensaje enviado con éxito a Telegram chat_id={cid}")
            else:
                logger.error(f"Error enviando mensaje a Telegram chat_id={cid}: HTTP {response.status_code} - {response.text}")
                overall_success = False
        except Exception as e:
            logger.error(f"Excepción al enviar mensaje a Telegram chat_id={cid}: {e}")
            overall_success = False

    return overall_success

def format_property_message(prop: dict) -> str:
    """Crea la plantilla de mensaje formateado HTML para Telegram."""
    source_emoji = {
        "Argenprop": "🔵 Argenprop",
        "Zonaprop": "🔴 Zonaprop",
        "MercadoLibre": "🟡 Mercado Libre"
    }.get(prop.get("source"), "🏠 " + prop.get("source", "Inmobiliaria"))

    msg = (
        f"<b>🏠 ¡NUEVO DEPARTAMENTO EN ALQUILER!</b>\n\n"
        f"<b>🌐 Portal:</b> {source_emoji}\n"
        f"<b>📍 Barrio:</b> {prop.get('location')}\n"
        f"<b>💰 Alquiler:</b> <code>{prop.get('price')}</code> (sin expensas)\n"
        f"<b>📋 Expensas:</b> {prop.get('expensas')}\n"
        f"<b>🏷️ Título:</b> {prop.get('title')}\n"
        f"<b>📍 Dirección:</b> {prop.get('address')}\n\n"
        f"🔗 <a href='{prop.get('url')}'><b>VER PUBLICACIÓN COMPLETA</b></a>"
    )
    return msg
