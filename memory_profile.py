import os
import sys
import time
import psutil
import threading
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('memory_monitor')

def log_memory_usage():
    """Registra o uso atual de memória do processo."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    # Converter para MB para facilitar a leitura
    rss_mb = mem_info.rss / (1024 * 1024)
    vms_mb = mem_info.vms / (1024 * 1024)
    
    logger.info(f"Memória: RSS={rss_mb:.2f}MB, VMS={vms_mb:.2f}MB")
    
    return rss_mb, vms_mb

def monitor_memory(interval=10):
    """Monitora o uso de memória em um intervalo regular."""
    while True:
        log_memory_usage()
        time.sleep(interval)  # intervalo em segundos

def start_memory_monitor():
    """Inicia o monitor de memória em uma thread separada."""
    thread = threading.Thread(target=monitor_memory, daemon=True)
    thread.start()
    logger.info("Monitor de memória iniciado")
    return thread

# Iniciar o monitor se este arquivo for importado
monitor_thread = None

def init_memory_monitor():
    global monitor_thread
    if monitor_thread is None:
        monitor_thread = start_memory_monitor()
