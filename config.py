import os

# Configuración del Bot de Telegram
# Reemplaza con tu TOKEN recibido de @BotFather y tu CHAT_ID obtenido de @userinfobot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Filtros de Búsqueda
MAX_PRICE = 950000  # En pesos argentinos (alquiler sin expensas)
LOCATIONS = ["Villa Devoto", "Villa Real"]

# Intervalo de Chequeo Automático (en minutos)
CHECK_INTERVAL_MINUTES = 10

# Archivo de Base de Datos para guardar publicaciones ya enviadas
DB_FILE = "seen_properties.db"
