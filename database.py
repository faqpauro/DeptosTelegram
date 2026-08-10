import sqlite3
import logging
from config import DB_FILE

logger = logging.getLogger(__name__)

def init_db():
    """Inicializa la tabla de propiedades vistas en SQLite."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_properties (
            id TEXT PRIMARY KEY,
            source TEXT,
            title TEXT,
            price TEXT,
            location TEXT,
            url TEXT,
            seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_property_seen(prop_id: str) -> bool:
    """Verifica si la propiedad ya fue registrada y notificada previamente."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM seen_properties WHERE id = ?", (prop_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_property_as_seen(prop_id: str, source: str, title: str, price: str, location: str, url: str):
    """Guarda una nueva propiedad en la base de datos."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO seen_properties (id, source, title, price, location, url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (prop_id, source, title, price, location, url))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error al guardar propiedad {prop_id} en la DB: {e}")
