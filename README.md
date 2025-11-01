🎵 Top Artistas Colombia – YouTube Charts

Este proyecto automatiza la extracción, análisis y visualización de los artistas más populares en*YouTube Charts Colombia, generando reportes detallados en Excel y gráficos en PDF.

---

🚀 Funcionalidad

El flujo completo consta de 3 scripts principales

1. **`extract_info_artists.py`**  
   - Extrae el ranking semanal de artistas desde [YouTube Charts](https://charts.youtube.com/charts/TopArtists/co/weekly).  
   - Guarda los resultados en `top_colombia_weekly_artists.csv`.

2. **`extract_info_per_artist.py`**  
   - Toma los 10 primeros artistas del CSV anterior.  
   - Accede a sus páginas individuales en YouTube Charts.  
   - Obtiene:
     - 📊 Visitas diarias recientes  
     - 🌍 Principales ciudades de audiencia  
     - 🎧 Canciones más escuchadas  
   - Genera un archivo `top10_artistas_detalle.xlsx` con una hoja por artista y categoría.

3. **`plotting_info_artist.py`**  
   - Lee el Excel y crea un PDF por artista con tres gráficos:
     - Evolución de visitas  
     - Ciudades más importantes  
     - Canciones más populares  
   - Los archivos se guardan en la carpeta `pdf_artistas#`.


   Se actualiza cada jueves a las 5:30 pm hora Colombia
