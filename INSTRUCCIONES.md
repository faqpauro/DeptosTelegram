# 🤖 Guía de Configuración - Bot de Alertas 24/7 en la Nube ($0 Costo)

Esta solución es **100% gratuita** y no requiere mantener tu computadora encendida.

---

## ⚡ Paso 1: Crear tu Bot de Telegram (1 minuto)

1. Abre tu aplicación de **Telegram**.
2. Busca el usuario oficial **`@BotFather`** o entra en [t.me/BotFather](https://t.me/BotFather).
3. Envía el comando `/newbot`.
4. Elige un nombre para tu bot (ej: `AlertasDevotoBot`).
5. Elige un nombre de usuario que termine en `bot` (ej: `AlertasDevoto_bot`).
6. Copia la clave **HTTP API Token** que te dará `@BotFather` (ej: `7123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

---

## 📱 Paso 2: Obtener tu CHAT ID (30 segundos)

1. En Telegram, entra a **`@userinfobot`** o abre [t.me/userinfobot](https://t.me/userinfobot).
2. Toca **Iniciar** y copia tu número de **Id** (ej: `123456789`).
3. **MUY IMPORTANTE:** Busca tu nuevo bot en Telegram y haz clic en **"Iniciar"** (o envíale `/start`) para autorizarlo a mandarte mensajes.

---

## ☁️ Paso 3: Dejar corriendo el Bot 24/7 en la Nube GRATIS (vía GitHub Actions)

Para que funcione **sin tener tu computadora prendida**, el bot se ejecutará gratis en la nube usando **GitHub Actions**:

1. Crea una cuenta gratuita en [GitHub.com](https://github.com) si no tienes una.
2. Crea un repositorio privado en GitHub (ej: `DeptosTelegram`).
3. Sube todos los archivos de esta carpeta a tu repositorio de GitHub.
4. En tu repositorio en GitHub, ve a **Settings** ➔ **Secrets and variables** ➔ **Actions**.
5. Haz clic en **New repository secret** y agrega dos secretos:
   - Secret 1: Name: `TELEGRAM_BOT_TOKEN` | Value: Tu token de BotFather.
   - Secret 2: Name: `TELEGRAM_CHAT_ID` | Value: Tu Chat ID de userinfobot.
6. ¡Listo! El archivo [scraper.yml](file:///c:/Develop/DeptosTelegram/.github/workflows/scraper.yml) se ejecutará automáticamente cada 20 minutos en los servidores de GitHub de forma totalmente **gratuita** las 24 horas del día.

---

## 💻 Paso 4: (Opcional) Probarlo en tu PC

Si quieres probarlo localmente en tu computadora antes de subirlo:

1. Edita `config.py` con tu Token y Chat ID.
2. Ejecuta la prueba de Telegram:
   ```bash
   python main.py --test-telegram
   ```
3. Ejecutar un escaneo manual:
   ```bash
   python main.py --once
   ```
