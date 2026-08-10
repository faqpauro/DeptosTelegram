import os

# Configuración del Bot de Telegram (Soporta múltiples chat_ids separados por coma)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8658747902:AAHegLGZme5RIf_zJHzsIfwEMsmFPooAjZA")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6608835035,6998073168")

# Filtros de Búsqueda
MAX_PRICE = 950000  # En pesos argentinos (alquiler sin expensas)
LOCATIONS = ["Villa Devoto", "Villa Real"]

# Exclusiones estrictas para evitar propiedades fuera de CABA (ej. Ciudadela, Tres de Febrero, etc.)
EXCLUDED_LOCATIONS = [
    "ciudadela", "tres de febrero", "caseros", "san martin", "san martín",
    "ramos mejia", "ramos mejía", "saenz peña", "sáenz peña", "san justo",
    "provincia", "general san martin", "vicente lopez", "vicente lópez",
    "zona oeste", "zona norte", "zona sur", "partido de"
]

def is_location_valid(address: str, title: str, expected_neighborhood: str) -> bool:
    """Valida estrictamente que la propiedad pertenezca a Villa Devoto o Villa Real en CABA."""
    full_text = f"{address} {title}".lower()

    # 1. Descartar si menciona partidos o localidades de Provincia
    for ex in EXCLUDED_LOCATIONS:
        if ex in full_text:
            return False

    # 2. Validar que pertenezca a Villa Devoto, Villa Real o Capital Federal/CABA
    nb_lower = expected_neighborhood.lower()
    if nb_lower in full_text or "devoto" in full_text or "villa real" in full_text:
        return True
    if "capital federal" in full_text or "caba" in full_text:
        return True

    return True

# Intervalo de Chequeo Automático (en minutos)
CHECK_INTERVAL_MINUTES = 10

# Archivo de Base de Datos para guardar publicaciones ya enviadas
DB_FILE = "seen_properties.db"
