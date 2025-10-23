import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import re

# === Función para nombres de hoja coherentes ===
def safe_sheet_name(base, suffix):
    name = re.sub(r'[\\/*?:\[\]]', '', base).strip()[:15]  # solo primeros 15 caracteres
    full_name = f"{name}_{suffix}"
    return full_name


archivo = "top10_artistas_detalle.xlsx"
xls = pd.ExcelFile(archivo)
os.makedirs("pdf_artistas", exist_ok=True)

# --- Detectar artistas automáticamente ---
artistas = {}
for sheet in xls.sheet_names:
    if "_" in sheet:
        artista, tipo = sheet.rsplit("_", 1)
        if artista not in artistas:
            artistas[artista] = {}
        artistas[artista][tipo] = sheet

# --- Generar PDFs ---
for artista, hojas in artistas.items():
    if all(k in hojas for k in ["visitas", "ciudades", "canciones"]):
        try:
            df_visitas = pd.read_excel(archivo, sheet_name=safe_sheet_name(artista, "visitas"))
            df_ciudades = pd.read_excel(archivo, sheet_name=safe_sheet_name(artista, "ciudades"))
            df_canciones = pd.read_excel(archivo, sheet_name=safe_sheet_name(artista, "canciones"))

            pdf_path = os.path.join("pdf_artistas", f"{artista.replace('/', '_')}.pdf")
            with PdfPages(pdf_path) as pdf:

                # --- Gráfico 1: Visitas ---
                plt.figure(figsize=(20,10))

                # Convertir fecha tipo "24 sep. 2025"
                df_visitas["Fecha"] = pd.to_datetime(
                    df_visitas["Fecha"].str.replace('.', '', regex=False),
                    format="%d %b %Y", errors='coerce'
                )
                df_visitas = df_visitas.dropna(subset=["Fecha"])
                df_visitas["Dia_Mes"] = df_visitas["Fecha"].dt.strftime("%d-%m")
                df_visitas["Año"] = df_visitas["Fecha"].dt.year

                sns.lineplot(data=df_visitas, x="Dia_Mes", y="Visitas")
                plt.xlabel(f"Año ({df_visitas['Año'].iloc[0]})")
                plt.xticks(rotation=45)
                plt.tight_layout()
                pdf.savefig()
                plt.close()


                # --- Gráfico 2: Ciudades ---
                plt.figure(figsize=(16,10))
                df_ciudades["Visitas"] = df_ciudades["Visitas"].astype(str)
                df_ciudades["Visitas"] = (
                    df_ciudades["Visitas"]
                    .str.replace('K', 'e3', regex=False)
                    .str.replace('M', 'e6', regex=False)
                    .apply(pd.eval)
                )
                df_ciudades.rename(columns={"Visitas": "Visitas(en millones)"}, inplace=True)
                sns.barplot(data=df_ciudades, x="Ciudad", y="Visitas(en millones)", hue="Ciudad")
                plt.xticks(rotation=45)
                plt.tight_layout()
                pdf.savefig()
                plt.close()

                # --- Gráfico 3: Canciones ---
                plt.figure(figsize=(16,10))
                df_canciones["Visitas"] = df_canciones["Visitas"].astype(str)
                df_canciones["Visitas"] = (
                    df_canciones["Visitas"]
                    .str.replace('K', 'e3', regex=False)
                    .str.replace('M', 'e6', regex=False)
                    .apply(pd.eval)
                )
                sns.barplot(data=df_canciones, y="Canción", x="Visitas", hue="Canción", legend=False)
                plt.tight_layout()
                pdf.savefig()
                plt.close()

            print(f"✅ PDF creado: {pdf_path}")

        except Exception as e:
            print(f"⚠️ Error con artista {artista}: {e}")
    else:
        print(f"⚠️ Saltando {artista}: faltan hojas completas")

print("✅ Todos los PDFs generados.")
