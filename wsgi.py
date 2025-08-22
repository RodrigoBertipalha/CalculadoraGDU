import os
from main import app, clean_all_files

# Limpa arquivos antigos na inicialização
clean_all_files()

# Configurações para melhorar desempenho em produção
if os.environ.get('PYTHONOPTIMIZE', '0') == '1':
    print("Rodando em modo de produção otimizado")

if __name__ == "__main__":
    app.run()