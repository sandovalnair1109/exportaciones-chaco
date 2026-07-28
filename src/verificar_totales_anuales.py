"""
Verifica el dato crudo de totales anuales de Chaco (2022-2025)
Fuente: opex_anexo_cuadros_10_03_26.xls, hoja 'OP-Regiones 2022-2025'
 
Correr desde la raíz del proyecto:
    python verificar_totales_anuales.py
"""
import pandas as pd

ARCHIVO = "data/raw/opex_anexo_cuadros_10_03_26.xls"
HOJA = "OP-Regiones 2022-2025"

df= pd.read_excel(ARCHIVO, sheet_name=HOJA, header=None)

encontrado=False
for i in range (len(df)):
    if str(df.iat[i,1]).strip()=="Chaco":
        print(f"Fila encontrada: {i}")
        print (df.iloc[i].tolist())
        encontrado=True

if not encontrado:
    print("No se encontró la fila 'Chaco'. Revisar nombre de hoja o columna")
    