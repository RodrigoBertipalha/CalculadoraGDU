import pandas as pd
import os
from datetime import datetime, timedelta

# Cria pasta para o arquivo de teste se não existir
test_folder = 'teste'
os.makedirs(test_folder, exist_ok=True)

# Criar dados de exemplo
data = {
    'ID': [1, 2, 3, 4, 5],
    'Descrição': ['Amostra 1', 'Amostra 2', 'Amostra 3', 'Amostra 4', 'Amostra 5'],
    'Data de Plantio': ['01/03/2025', '15/03/2025', '01/04/2025', '15/04/2025', '01/05/2025'],
    '05. SFWD': ['15/05/2025', '01/06/2025', '15/06/2025', '01/07/2025', '15/07/2025'],
    '06. PFWD': ['10/05/2025', '25/05/2025', '10/06/2025', '25/06/2025', '10/07/2025']
}

# Criar DataFrame
df = pd.DataFrame(data)

# Salvar o arquivo Excel para teste
output_path = os.path.join(test_folder, 'teste_datas_brasileiras.xlsx')
df.to_excel(output_path, index=False)

print(f"Arquivo de teste criado em: {output_path}")
print("Use este arquivo para testar a aplicação GDU no navegador.")
