"""
Verifica el dato derivado del primer semestre de Chaco (2021-2026)
Fuente: Serie_Opex_Mensual_2002_2026.xlsx
Hoja: Serie_Opex_Mensual_2002_2026_06

Nombres de columna CONFIRMADOS sobre el archivo real (28/07/2026):
    Año, Mes, FOB_dólar, Peso neto, Nombre Prov, Nombre_Región, Rubro

Correr desde la raíz del proyecto:
    python verificar_primer_semestre.py
"""
import pandas as pd

ARCHIVO = "data/raw/exports_2026_M/Serie_Opex_Mensual_2002_2026.xlsx"
HOJA = "Serie_Opex_Mensual_2002_2026_06"

df = pd.read_excel(ARCHIVO, sheet_name=HOJA)
df["Año"] = df["Año"].astype(int)
df["Mes"] = df["Mes"].astype(int)

chaco = df[df["Nombre Prov"].astype(str).str.strip() == "Chaco"]
primer_semestre = chaco[chaco["Mes"] <= 6]

usd = primer_semestre.groupby("Año")["FOB_dólar"].sum() / 1_000_000
ton = primer_semestre.groupby("Año")["Peso neto"].sum() / 1000

print("Primer semestre - USD (millones) por año:")
print(usd.round(1))
print()
print("Primer semestre - Toneladas por año:")
print(ton.round(0))