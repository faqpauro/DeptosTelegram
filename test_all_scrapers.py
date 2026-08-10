import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from scrapers.argenprop import fetch_argenprop
from scrapers.zonaprop import fetch_zonaprop
from scrapers.mercadolibre import fetch_mercadolibre

print("=" * 60)
print("🧪 TEST DE VERIFICACION DE SCRAPERS INDIVIDUALES")
print("=" * 60)

print("\n📡 1. Probando ARGENPROP...")
items_arg = fetch_argenprop()
print(f"✅ Argenprop trajo {len(items_arg)} departamentos válidos:")
for item in items_arg[:3]:
    print(f"   • [{item['location']}] {item['title']} - {item['price']} ({item['expensas']})")
    print(f"     URL: {item['url']}")

print("\n📡 2. Probando ZONAPROP...")
items_zp = fetch_zonaprop()
print(f"✅ Zonaprop trajo {len(items_zp)} departamentos válidos:")
for item in items_zp[:3]:
    print(f"   • [{item['location']}] {item['title']} - {item['price']} ({item['expensas']})")
    print(f"     URL: {item['url']}")

print("\n📡 3. Probando MERCADO LIBRE...")
items_ml = fetch_mercadolibre()
print(f"✅ Mercado Libre trajo {len(items_ml)} departamentos válidos:")
for item in items_ml[:3]:
    print(f"   • [{item['location']}] {item['title']} - {item['price']}")
    print(f"     URL: {item['url']}")

print("\n" + "=" * 60)
print(f"📊 RESUMEN FINAL: {len(items_arg)} de Argenprop, {len(items_zp)} de Zonaprop, {len(items_ml)} de MercadoLibre")
print("=" * 60)
