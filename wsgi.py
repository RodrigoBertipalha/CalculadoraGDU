import os
import sys
from main import app, clean_all_files

# Limpa arquivos antigos na inicialização
clean_all_files()

# Configurações para melhorar desempenho em produção
if os.environ.get('PYTHONOPTIMIZE', '0') == '1':
    print("Rodando em modo de produção otimizado")

# Configuração para reduzir uso de memória
os.environ["OPENPYXL_NOTHREADED"] = "1"  # Desativa threads do openpyxl
os.environ["OMP_NUM_THREADS"] = "1"      # Limita threads OpenMP
os.environ["NUMEXPR_MAX_THREADS"] = "1"  # Limita threads NumExpr

# Configurações para reduzir uso de memória no pandas/numpy
try:
    import pandas as pd
    import numpy as np
    # Configurar pandas para usar menos memória
    pd.options.mode.chained_assignment = None
    # Reduzir tamanho do pool de strings
    pd.options.mode.string_storage = 'python'
except ImportError:
    print("Pandas ou NumPy não disponíveis no ambiente.")

# Força coleta de lixo
try:
    import gc
    gc.collect()
    gc.enable()
except ImportError:
    pass

if __name__ == "__main__":
    app.run()