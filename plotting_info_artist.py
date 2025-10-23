import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import re

def safe_sheet_name(base, suffix):
    name = re.sub(r'[\\/*?:\[\]]', '', base).strip()[:15]
    return f"{name}_{suffix}"

archivo = "top10_artistas_detalle.xlsx"
xls = pd.ExcelFile(archivo)
os.makedirs("pdf_artistas", exist_ok=True)

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

            pdf_path = os.path.join("pdf_artistas", f"{artista.replace('/', '_')}.pdf")
            with PdfPages(pdf_path) as pdf:
                # --- Gráfico 1: Visitas ---
                plt.figure(figsize=(20, 10))
                df_visitas["Fecha"] = pd.to_datetime(
                    df_visitas["Fecha"].str.replace('.', '', regex=False),
                    format="%d %b %Y", errors="coerce"
                )
                df_visitas = df_visitas.dropna(subset=["Fecha"])
                if df_visitas.empty:
                    print(f"⚠️ Sin fechas válidas para {artista}")
                    continue
                df_visitas["Dia_Mes"] = df_visitas["Fecha"].dt.strftime("%d-%m")
                df_visitas["Año"] = df_visitas["Fecha"].dt.year
                sns.lineplot(data=df_visitas, x="Dia_Mes", y="Visitas")
                plt.title(f"Visitas Diarias - {artista}")
                plt.xlabel(f"Año ({df_visitas['Año'].iloc[0]})")
                plt.xticks(rotation=45)
                plt.tight_layout()
                pdf.savefig()
                plt.close()

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

            print(f"✅ PDF creado: {pdf_path}")
        except Exception as e:
            print(f"⚠️ Error con artista {artista}: {e}")
    else:
        print(f"⚠️ Saltando {artista}: faltan hojas completas")

print("✅ Todos los PDFs generados.")
