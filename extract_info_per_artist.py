from playwright.sync_api import sync_playwright
import pandas as pd
import re
import time

def safe_sheet_name(base, suffix):
    # Quitar caracteres inválidos para Excel
    name = re.sub(r'[\\/*?:\[\]]', '', base).strip()[:14]  # solo primeros 14 caracteres

    full_name = f"{name}_{suffix}"
    return full_name

# Leer CSV con artistas y URLs
df = pd.read_csv("top_colombia_weekly_artists.csv")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page()

    # Crear archivo Excel
    with pd.ExcelWriter("top10_artistas_detalle.xlsx", engine="xlsxwriter") as writer:
        # Solo top 10 artistas
        for index, row in df.head(10).iterrows():
            artista = row["name"]
            url = row["url_tarjeta"]

            print(f"Extrayendo datos de: {artista}")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(8000)  # esperar a que cargue la página

                # ====================
                # 1) Visitas diarias
                # ====================
                try:
                    page.wait_for_selector('ytmc-views-card-v2', timeout=5000)
                    oyentes = page.query_selector('ytmc-views-card-v2')
                    texto = oyentes.inner_text()
                    patron_fechas = r"(\d{1,2} \w+\.? \d{4})\s+([\d,.]+)"
                    datos_visitas = re.findall(patron_fechas, texto)[1:]  # quitar encabezado
                    df_visitas = pd.DataFrame(datos_visitas, columns=["Fecha", "Visitas"])
                except:
                    df_visitas = pd.DataFrame(columns=["Fecha", "Visitas"])

                # ====================
                # 2) Top 10 ciudades
                # ====================
                try:
                    ciudades = page.query_selector_all('.entityTitleForInsightsPageLocationEntity')
                    vistas_ciudades = page.query_selector_all('.subtitleForInsightsPageLocationEntity')
                    lista_ciudades = []
                    for c, v in zip(ciudades, vistas_ciudades):
                        ciudad = c.inner_text().strip()
                        vistas = v.inner_text().replace(" vistas", "").strip()
                        lista_ciudades.append([ciudad, vistas])
                    df_ciudades = pd.DataFrame(lista_ciudades[:10], columns=["Ciudad", "Visitas"])
                except:
                    df_ciudades = pd.DataFrame(columns=["Ciudad", "Visitas"])

                # ====================
                # 3) Top 10 canciones
                # ====================
                try:
                    canciones = page.query_selector_all('img.thumbForInsightsPageSongEntity')
                    vistas_canciones = page.query_selector_all('.viewscount')
                    lista_canciones = []
                    for c, v in zip(canciones, vistas_canciones):
                        nombre = c.get_attribute('aria-label').strip()
                        vistas = v.inner_text().replace(" vistas", "").strip()
                        lista_canciones.append([nombre, vistas])
                    df_canciones = pd.DataFrame(lista_canciones[:10], columns=["Canción", "Visitas"])
                except:
                    df_canciones = pd.DataFrame(columns=["Canción", "Visitas"])

                # ====================
                # Guardar hojas en Excel
                # ====================
                df_visitas.to_excel(writer, sheet_name=safe_sheet_name(artista, "visitas"), index=False)
                df_ciudades.to_excel(writer, sheet_name=safe_sheet_name(artista, "ciudades"), index=False)
                df_canciones.to_excel(writer, sheet_name=safe_sheet_name(artista, "canciones"), index=False)

                time.sleep(1)  # pequeña pausa entre artistas

            except Exception as e:
                print(f"❌ Error al procesar {artista}: {e}")

    browser.close()

print("✅ Archivo 'top10_artistas_detalle.xlsx' generado correctamente.")
