from main import app

if __name__ == "__main__":
    app.run()

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