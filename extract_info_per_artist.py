from playwright.sync_api import sync_playwright
import pandas as pd
import re
import time

def safe_sheet_name(base, suffix):
    # Quitar caracteres inválidos para Excel
    name = re.sub(r'[\\/*?:\[\]]', '', base).strip()[:14]
    full_name = f"{name}_{suffix}"
    return full_name



def limpiar_texto_vistas(texto):
    """Elimina las palabras 'views', 'vistas', 'visualizaciones' y espacios."""
    return (
        texto.replace("views", "")
             .replace("vistas", "")
             .replace("visualizaciones", "")
             .replace("visualization", "")
             .strip()
    )


# Leer CSV con artistas y URLs
df = pd.read_csv("top_colombia_weekly_artists.csv")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(
        locale="es-ES",
        timezone_id="America/Bogota",
        geolocation={"latitude": 4.711, "longitude": -74.0721},
        permissions=["geolocation"],
        extra_http_headers={
            "Accept-Language": "es-ES,es;q=0.9"
        }
    )
    page = browser.new_page()

    with pd.ExcelWriter("top10_artistas_detalle.xlsx", engine="xlsxwriter") as writer:
        for index, row in df.head(10).iterrows():
            artista = row["name"]
            url = row["url_tarjeta"]

            print(f"\n🎵 Extrayendo datos de: {artista}")
            try:
                page.goto(url, timeout=120000)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(5)

                # ====================
                # 1) Visitas diarias
                # ====================
                try:
                    page.wait_for_selector('ytmc-views-card-v2', timeout=10000)
                    oyentes = page.query_selector('ytmc-views-card-v2')
                    if oyentes:
                        texto = oyentes.inner_text()
                        patron_fechas = r"(\d{1,2} \w+\.? \d{4})\s+([\d,.]+)"
                        datos_visitas = re.findall(patron_fechas, texto)[1:]
                        df_visitas = pd.DataFrame(datos_visitas, columns=["Fecha", "Visitas"])
                    else:
                        print("⚠️ No se encontró bloque de visitas")
                        df_visitas = pd.DataFrame(columns=["Fecha", "Visitas"])
                except Exception as e:
                    print(f"⚠️ Error al extraer visitas: {e}")
                    df_visitas = pd.DataFrame(columns=["Fecha", "Visitas"])

                # ====================
                # 2) Top 10 ciudades
                # ====================
                try:
                    page.wait_for_selector('.entityTitleForInsightsPageLocationEntity', timeout=8000)
                    ciudades = page.query_selector_all('.entityTitleForInsightsPageLocationEntity')
                    vistas_ciudades = page.query_selector_all('.subtitleForInsightsPageLocationEntity')
                    lista_ciudades = []
                    for c, v in zip(ciudades, vistas_ciudades):
                        ciudad = c.inner_text().strip()
                        vistas = limpiar_texto_vistas(v.inner_text())
                        lista_ciudades.append([ciudad, vistas])
                    df_ciudades = pd.DataFrame(lista_ciudades[:10], columns=["Ciudad", "Visitas"])
                except Exception as e:
                    print(f"⚠️ Error al extraer ciudades: {e}")
                    df_ciudades = pd.DataFrame(columns=["Ciudad", "Visitas"])

                # ====================
                # 3) Top 10 canciones
                # ====================
                try:
                    page.wait_for_selector('img.thumbForInsightsPageSongEntity', timeout=8000)
                    canciones = page.query_selector_all('img.thumbForInsightsPageSongEntity')
                    vistas_canciones = page.query_selector_all('.viewscount')
                    lista_canciones = []
                    for c, v in zip(canciones, vistas_canciones):
                        nombre = c.get_attribute('aria-label') or "Desconocida"
                        vistas = limpiar_texto_vistas(v.inner_text())
                        lista_canciones.append([nombre.strip(), vistas])
                    df_canciones = pd.DataFrame(lista_canciones[:10], columns=["Canción", "Visitas"])
                except Exception as e:
                    print(f"⚠️ Error al extraer canciones: {e}")
                    df_canciones = pd.DataFrame(columns=["Canción", "Visitas"])

                # ====================
                # Guardar en Excel
                # ====================
                df_visitas.to_excel(writer, sheet_name=safe_sheet_name(artista, "visitas"), index=False)
                df_ciudades.to_excel(writer, sheet_name=safe_sheet_name(artista, "ciudades"), index=False)
                df_canciones.to_excel(writer, sheet_name=safe_sheet_name(artista, "canciones"), index=False)

                print(f"✅ Datos guardados para {artista}")
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error al procesar {artista}: {e}")

    browser.close()

print("\n✅ Archivo 'top10_artistas_detalle.xlsx' generado correctamente.")

