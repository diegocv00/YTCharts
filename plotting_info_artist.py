import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import re

def safe_sheet_name(base, suffix):
    name = re.sub(r'[\\/*?:\[\]]', '', base).strip()[:15]
    return f"{name}_{suffix}"

# Permitir que la carpeta de salida sea pasada como argumento
output_folder = sys.argv[1] if len(sys.argv) > 1 else "pdf_artistas"
os.makedirs(output_folder, exist_ok=True)

archivo = "top10_artistas_detalle.xlsx"
xls = pd.ExcelFile(archivo)

artistas = {}
for sheet in xls.sheet_names:
    if "_" in sheet:
        artista, tipo = sheet.rsplit("_", 1)
        artistas.setdefault(artista, {})[tipo] = sheet

for artista, hojas in artistas.items():
    if all(k in hojas for k in ["visitas", "ciudades", "canciones"]):
        try:
            df_visitas = pd.read_excel(archivo, sheet_name=hojas["visitas"])
            df_ciudades = pd.read_excel(archivo, sheet_name=hojas["ciudades"])
            df_canciones = pd.read_excel(archivo, sheet_name=hojas["canciones"])

            if df_visitas.empty or df_ciudades.empty or df_canciones.empty:
                print(f"⚠️ Saltando {artista}: datos incompletos")
                continue

            # Guardar PDFs en la carpeta de salida 
            pdf_path = os.path.join(output_folder, f"{artista.replace('/', '_')}.pdf")
            with PdfPages(pdf_path) as pdf:
                
                # --- Gráfico 1: Visitas ---
                plt.figure(figsize=(20,10))

                # Diccionario para traducir meses de Español a Inglés
                meses_map = {
                    'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 
                    'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 
                    'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
                }

                # Función auxiliar para limpiar y traducir la fecha
                def limpiar_fecha(fecha):
                    if pd.isna(fecha): return fecha
                    fecha = str(fecha).replace('.', '').lower() # Quitar puntos y pasar a minúsculas
                    for mes_es, mes_en in meses_map.items():
                        if mes_es in fecha:
                            return fecha.replace(mes_es, mes_en)
                    return fecha

                # 1. Aplicar la traducción
                df_visitas["Fecha_Str"] = df_visitas["Fecha"].apply(limpiar_fecha)

                # 2. Convertir a datetime usando los meses en inglés
                df_visitas["Fecha"] = pd.to_datetime(
                    df_visitas["Fecha_Str"], 
                    format="%d %b %Y", 
                    errors='coerce'
                )
                
                # Verificar si hay datos válidos antes de graficar
                df_visitas = df_visitas.dropna(subset=["Fecha"])
                
                if not df_visitas.empty:
                    # Ordenar por fecha para que la línea no salga garabateada
                    df_visitas = df_visitas.sort_values("Fecha")
                    
                    df_visitas["Dia_Mes"] = df_visitas["Fecha"].dt.strftime("%d-%m")
                    
                    sns.lineplot(data=df_visitas, x="Dia_Mes", y="Visitas")
                    plt.title(f"Visitas Diarias - {artista}")
                    plt.xlabel("Fecha")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    pdf.savefig()
                    plt.close()
                else:
                    print(f"⚠️ Aviso: No se pudieron procesar las fechas para {artista} (Gráfico de visitas vacío).")

                # --- Gráfico 2: Ciudades ---
                plt.figure(figsize=(16, 10))
                df_ciudades["Visitas"] = (
                    df_ciudades["Visitas"].astype(str)
                    .str.replace('K', 'e3', regex=False)
                    .str.replace('M', 'e6', regex=False)
                    .apply(pd.eval)
                )
                sns.barplot(data=df_ciudades, x="Ciudad", y="Visitas", hue="Ciudad", legend=False)
                plt.title(f"Top 10 Ciudades - {artista}")
                plt.xticks(rotation=45)
                plt.tight_layout()
                pdf.savefig()
                plt.close()

                # --- Gráfico 3: Canciones ---
                plt.figure(figsize=(16, 10))
                df_canciones["Visitas"] = (
                    df_canciones["Visitas"].astype(str)
                    .str.replace('K', 'e3', regex=False)
                    .str.replace('M', 'e6', regex=False)
                    .apply(pd.eval)
                )
                sns.barplot(data=df_canciones, y="Canción", x="Visitas", hue="Canción", legend=False)
                plt.title(f"Top 10 Canciones - {artista}")
                plt.tight_layout()
                pdf.savefig()
                plt.close()

            print(f"PDF creado: {pdf_path}")
        except Exception as e:
            print(f"Error con artista {artista}: {e}")
    else:
        print(f"Saltando {artista}: faltan hojas completas")

print("Todos los PDFs generados.")


