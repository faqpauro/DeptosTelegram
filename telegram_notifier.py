import logging
import requests

logger = logging.getLogger(__name__)

def send_telegram_message(bot_token: str, chat_id: str, message_html: str) -> bool:
    """Envía un mensaje formateado con HTML a Telegram."""
    if not bot_token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no estan configurados en config.py")
        print("[!] ALERTA: No has configurado TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en config.py aun.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"Mensaje enviado con éxito a Telegram chat_id={chat_id}")
            return True
        else:
            logger.error(f"Error enviando mensaje a Telegram: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Excepción al enviar mensaje a Telegram: {e}")
        return False

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
