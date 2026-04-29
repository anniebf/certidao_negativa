import logging
import logging.handlers
import os
from datetime import datetime

# Criar diretório de logs se não existir
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configurar nome do arquivo de log com data
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def setup_logger(name):
    """
    Configura um logger com handlers para arquivo e console
    
    Args:
        name (str): Nome do logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remover handlers existentes para evitar duplicação
    if logger.handlers:
        logger.handlers.clear()
    
    # Formato de log detalhado
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    
    # Handler para arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger
