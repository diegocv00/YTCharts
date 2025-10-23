# importar librerias
from playwright.sync_api import sync_playwright
import pandas as pd
import re

patron = r'/([gm])/([^\\]+)'


#iniciar playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # lanzar el navegador chrome en modo oculto
    page = browser.new_page()

    #definimos url a scrapear
    url = "https://charts.youtube.com/charts/TopArtists/co/weekly"
    page.goto(url)

    # Esperar a que cargue el contenido de la seccion que queremos scrapear
    page.wait_for_selector('ytmc-chart-table-v2 div')

    #extraer los artistas que estan todos en lista con ytmc-entry-row
    artists = page.query_selector_all('ytmc-entry-row')
    

    #creamos una lista vacia para almacenar el top
    top_colombia_weekly =[]

    for artist in artists:
        name = artist.query_selector('span.artistName')
        top = artist.query_selector_all('div.metric.content.center')
        link = name.get_attribute('endpoint') if name else ""
    
        resultado = re.search(patron, link)

        namef = name.inner_text() if name else "N/A"
        top_position = top[1].inner_text() if len(top) > 1 else "N/A"
        weeks_in_top = top[2].inner_text() if len(top) > 2 else "N/A"
        weekly_views = top[3].inner_text() if len(top) > 3 else "N/A"

        if resultado:
            tipo = resultado.group(1)       # 'g' o 'm'
            artista_id = resultado.group(2) # el ID real
            url_tarjeta = f"https://charts.youtube.com/artist/%2F{tipo}%2F{artista_id}"
        else:
            url_tarjeta = "N/A"

        top_colombia_weekly.append({
            "top_position": top_position,
            "name": namef,
            "weeks_in_top": weeks_in_top,
            "weekly_views": weekly_views,
            "url_tarjeta": url_tarjeta
    })

    
    #print(top_colombia_weekly)
    #convertir a dataframe
    df_top_artists = pd.DataFrame(top_colombia_weekly)
    #print(df_top_artists.head())
    df_top_artists.to_csv("top_colombia_weekly_artists.csv", index=False)


    browser.close()  # Cerrar el navegador
