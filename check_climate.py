import pandas as pd

# Carregar o arquivo climático
df = pd.read_excel("base_clima/temperaturas_2025.xlsx", sheet_name="Fonte  Estação Terra Nova Temp.")

# Converter a coluna de data para datetime
df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

# Mostrar informações sobre o arquivo
print(f"Primeiras 5 linhas:\n{df.head()}\n")
print(f"Intervalo de datas: de {df["data"].min()} até {df["data"].max()}")
print(f"Número total de registros: {len(df)}")
print(f"Colunas disponíveis: {df.columns.tolist()}")

# Verificar valores nulos
print(f"\nValores nulos por coluna:\n{df.isna().sum()}")

# Verificar a distribuição dos meses
print(f"\nDistribuição dos meses:\n{df["data"].dt.month.value_counts().sort_index()}")