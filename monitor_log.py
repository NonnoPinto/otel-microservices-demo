import time
import shutil
import os
from datetime import datetime

LOG_FILE = "collector.log"
CHECK_INTERVAL = 1  # Ogni quanti secondi controllare il file
MAX_LINES = 10000  # Numero massimo di righe prima di ruotare il log

def count_lines(filepath):
    """Conta le righe di un file in modo efficiente."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)

def rotate_log():
    """Crea una copia del log con timestamp e svuota il file originale."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"./bk/{LOG_FILE}_{timestamp}.log"
    
    shutil.copy(LOG_FILE, backup_file)  # Copia il file con il nuovo nome
    open(LOG_FILE, "w").close()  # Svuota il file originale
    
    print(f"[{timestamp}] Log salvato come {backup_file} e resettato.")

def monitor_log():
    """Monitora il file di log e lo ruota quando supera il limite."""
    while True:
        if os.path.exists(LOG_FILE):
            line_count = count_lines(LOG_FILE)
            if line_count >= MAX_LINES:
                rotate_log()
        time.sleep(CHECK_INTERVAL)  # Aspetta prima di controllare di nuovo

if __name__ == "__main__":
    print("Monitor log avviato...")
    monitor_log()
