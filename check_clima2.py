import pandas as pd

# Carregar o arquivo climático
df = pd.read_excel('base_clima/temperaturas_2025.xlsx', sheet_name='Fonte  Estação Terra Nova Temp.')

# Converter a coluna de data para datetime
df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')

# Mostrar informações sobre o arquivo
print("Primeiras 5 linhas:")
print(df.head())
print("\nIntervalo de datas:")
print(f"De: {df['data'].min()}")
print(f"Até: {df['data'].max()}")
print(f"\nNúmero total de registros: {len(df)}")
print("\nColunas disponíveis:")
print(df.columns.tolist())

# Verificar valores nulos
print("\nValores nulos por coluna:")
print(df.isna().sum())

# Verificar a distribuição dos meses
print("\nDistribuição dos meses:")
meses = df['data'].dt.month.value_counts().sort_index()
for mes, count in meses.items():
    print(f"Mês {mes}: {count} registros")
