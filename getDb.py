from dotenv import load_dotenv
import oracledb
import os
from logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()
username = os.getenv('usernamedb')
password = os.getenv('password')
dsn = os.getenv('dsn')

def resultado():

    try:
        logger.info("Iniciando conexão com banco de dados Oracle")
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        logger.debug(f"Conectado ao DSN: {dsn}")
        
        cursor = connection.cursor()
        logger.info("Executando query para buscar CNPJs")
        
        cursor.execute("""
            SELECT M0_CGC from PROTHEUS11.sigaemp 
            WHERE LENGTH(trim(M0_CGC)) >= 12
        """)
        resultado = cursor.fetchall()
        
        logger.info(f"Total de {len(resultado)} CNPJs recuperados do banco")
        connection.close()
        
        return resultado
        
    except oracledb.DatabaseError as e:
        logger.error(f"Erro de banco de dados: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar CNPJs: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Iniciando script getDb.py")
        cnpjs = resultado()
        logger.info(f"Script finalizado com sucesso. {len(cnpjs)} CNPJs encontrados")
    except Exception as e:
        logger.critical(f"Script falhou: {e}")