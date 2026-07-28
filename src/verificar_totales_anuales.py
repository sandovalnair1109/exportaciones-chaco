"""
Verifica el dato crudo de totales anuales de Chaco (2022-2025)
Fuente: opex_anexo_cuadros_10_03_26.xls, hoja 'OP-Regiones 2022-2025'
 
Uso desde notebook:
    %run ../src/verificar_totales_anuales.py
"""
import pandas as pd
from pathlib import Path

# Detectamos raíz del proyecto
RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "raw" / "opex_anexo_cuadros_10_03_26.xls"
HOJA = "OP-Regiones 2022-2025"

df = pd.read_excel(ARCHIVO, sheet_name=HOJA, header=None)

print("=" * 70)
print("TOTALES ANUALES OFICIALES (INDEC)")
print("Provincia: Chaco")
print(f"Fuente: {ARCHIVO.name}")
print(f"Hoja:   {HOJA}")
print("=" * 70)

encontrado=False
for i in range (len(df)):
    if str(df.iat[i,1]).strip()=="Chaco":
        fila = df.iloc[i]
        
        # Estructura REAL confirmada de esta hoja (verificado corriendo el
        # script y comparando contra el PDF del informe técnico OPEX):
        # col 0 = vacío, col 1 = Provincia,
        # col 2 a 5 = años 2022, 2023, 2024, 2025 (en millones de USD FOB)
        # col 6 = variación % 2025 vs 2024
        # col 7 = variación % 2025 vs 2022
        # NO son años 2026/2027 — son columnas de variación porcentual.
        años = [2022, 2023, 2024, 2025]
        valores_anuales = fila.iloc[2:6].values
        variacion_vs_2024 = fila.iloc[6]
        variacion_vs_2022 = fila.iloc[7]
        
        print(f"\nFila índice {i} en el Excel:\n")
        print(f"{'Año':<10} {'Valor (miles USD FOB)':>25}")
        print("-" * 38)
        
        for año, valor in zip(años, valores_anuales):
            if pd.isna(valor):
                val_str = "—"
            else:
                val_str = f"{valor:>25,.2f}"
            
            # Destacamos 2024 porque es el que vamos a comparar con microdatos
            marca = "  ← COMPARAR CON MICRODATOS 2024" if año == 2024 else ""
            print(f"{año:<10} {val_str}{marca}")

        print()
        print(f"Variación % 2025 vs 2024: {variacion_vs_2024:+.2f}%")
        print(f"Variación % 2025 vs 2022: {variacion_vs_2022:+.2f}%")

        encontrado = True
        break

if not encontrado:
    print("\n❌ No se encontró la fila 'Chaco'.")
    print("   Revisar: nombre de hoja, o que la columna B tenga 'Chaco'.")
