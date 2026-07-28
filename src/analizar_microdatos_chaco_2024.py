"""
Análisis exploratorio de microdatos OPEX — Chaco (2024)
Fuente: Datos_origen_2024_mayo_2025.xlsx, hoja 'Datos Opex Año 2024'

Correr desde cualquier lugar:
    python src/analizar_microdatos_chaco_2024.py
    o desde notebook: %run ../src/analizar_microdatos_chaco_2024.py
"""
import pandas as pd
from pathlib import Path

# Detectamos la raíz del proyecto (donde está la carpeta src/)
RAIZ = Path(__file__).resolve().parents[1]

ARCHIVO = RAIZ / "data" / "raw" / "exports_2024_Y" / "Datos_origen_2024_mayo_2025.xlsx"
HOJA = "Datos Opex Año 2024"

df = pd.read_excel(ARCHIVO, sheet_name=HOJA)

print("=" * 60)
print("ESTRUCTURA GENERAL DEL ARCHIVO")
print("=" * 60)
print(f"Total de filas:        {len(df)}")
print(f"Columnas:              {list(df.columns)}")
print(f"Meses presentes:       {sorted(df['CMES'].dropna().unique())}")
print(f"Años presentes:        {sorted(df['CANIO'].dropna().unique())}")
print(f"Provincias:            {df['DESCRIP_PCIA'].nunique()}")
print()

# --- FILTRO CHACO ---
chaco = df[df["DESCRIP_PCIA"].astype(str).str.strip() == "Chaco"].copy()

total_chaco = chaco["DOLARES_FOB"].sum()
total_kg = chaco["PESO_NETO_KG"].sum()

print("=" * 60)
print("CHACO — RESUMEN AGREGADO")
print("=" * 60)
print(f"Filas:                 {len(chaco)}")
print(f"DOLARES_FOB total:     ${total_chaco:,.2f}")
print(f"PESO_NETO_KG total:    {total_kg:,.2f}")
print()

# --- RUBROS ---
print("=" * 60)
print("CHACO — RUBROS (por DOLARES_FOB)")
print("=" * 60)
rubros = chaco.groupby("DESCRIP_RUBRO")["DOLARES_FOB"].sum().sort_values(ascending=False)
for rubro, valor in rubros.head(10).items():
    pct = valor / total_chaco * 100
    print(f"{rubro[:48]:<48} ${valor/1_000_000:>9.2f} M  ({pct:>5.1f}%)")
print()

# --- PAÍSES DESTINO ---
print("=" * 60)
print("CHACO — PAÍSES DESTINO (por DOLARES_FOB)")
print("=" * 60)
paises = chaco.groupby("DESCRIP_PAIS")["DOLARES_FOB"].sum().sort_values(ascending=False)
for pais, valor in paises.head(10).items():
    pct = valor / total_chaco * 100
    print(f"{pais[:35]:<35} ${valor/1_000_000:>9.2f} M  ({pct:>5.1f}%)")
print()

# --- RUBROS CON LA PALABRA "CONFIDENCIAL" ---
print("=" * 60)
print("CHACO — REGISTROS CON RUBRO CONFIDENCIAL")
print("=" * 60)
confid = chaco[chaco["DESCRIP_RUBRO"].str.contains("confidencial|Confidencial", case=False, na=False)]
print(f"Cantidad de filas:{len(confid)}")
print(f"Suma DOLARES_FOB:${confid['DOLARES_FOB'].sum():,.2f}")
print()

# --- PRECIO POR KG (rubros principales) ---
print("=" * 60)
print("CHACO — PRECIO PROMEDIO USD/KG (top 5 rubros por valor)")
print("=" * 60)
chaco["precio_kg"] = chaco["DOLARES_FOB"] / chaco["PESO_NETO_KG"]
precios = chaco.groupby("DESCRIP_RUBRO").agg({
    "DOLARES_FOB": "sum",
    "PESO_NETO_KG": "sum"
}).sort_values("DOLARES_FOB", ascending=False).head(5)
precios["usd_por_kg"] = precios["DOLARES_FOB"] / precios["PESO_NETO_KG"]
for rubro, row in precios.iterrows():
    print(f"{rubro[:40]:<40} ${row['usd_por_kg']:.3f}/kg")
print()

# --- TOP REGISTROS INDIVIDUALES ---
print("=" * 60)
print("CHACO — TOP 10 REGISTROS INDIVIDUALES (mayor DOLARES_FOB)")
print("=" * 60)
top10 = chaco.nlargest(10, "DOLARES_FOB")[["DESCRIP_RUBRO", "DESCRIP_PAIS", "DOLARES_FOB", "PESO_NETO_KG"]]
for idx, row in top10.iterrows():
    rubro = row["DESCRIP_RUBRO"][:35]
    pais = row["DESCRIP_PAIS"][:20]
    print(f"{rubro:<35} | {pais:<20} | ${row['DOLARES_FOB']:>14,.2f}")