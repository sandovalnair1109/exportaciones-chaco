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
        
        # Asumimos estructura: col 0 = índice/orden, col 1 = Provincia,
        # col 2 en adelante = años 2022, 2023, 2024, 2025...
        años = list(range(2022, 2022 + len(fila) - 2))
        valores = fila.iloc[2:].values
        
        print(f"\nFila índice {i} en el Excel:\n")
        print(f"{'Año':<10} {'Valor (miles USD FOB)':>25}")
        print("-" * 38)
        
        for año, valor in zip(años, valores):
            if pd.isna(valor):
                val_str = "—"
            else:
                val_str = f"{valor:>25,.2f}"
            
            # Destacamos 2024 porque es el que vamos a comparar con microdatos
            marca = "  ← COMPARAR CON MICRODATOS 2024" if año == 2024 else ""
            print(f"{año:<10} {val_str}{marca}")
        
        encontrado = True
        break

if not encontrado:
    print("\n❌ No se encontró la fila 'Chaco'.")
    print("   Revisar: nombre de hoja, o que la columna B tenga 'Chaco'.")
