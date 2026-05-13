from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import getDb
import shutil
import os
import json
from time import sleep, time
from logger import setup_logger
import getInfosPdf
from api_client import APIClient

logger = setup_logger(__name__)

url = "https://www.sefaz.mt.gov.br/cnd/certidao/servlet/ServletRotdAberto?origem=60"
diretorio_pdf = fr"C:\certidao_negativa\download"
pasta_final_pdf = fr"C:\certidao_negativa\pdf"

# ========================================================
# INICIALIZAR CLIENTE DA API UMA VEZ (reutilizado no loop)
# ========================================================
# Esta instância será reutilizada para enviar MÚLTIPLOS JSONs
# A cada iteração do loop, ela envia um JSON diferente
api_client = APIClient()
logger.info("Cliente da API inicializado com as configurações:")
logger.info(f"  - URL: http://10.192.0.193:8885/rest/BFFS01FF/")
logger.info(f"  - Usuário: Admin")
logger.info(f"  - Tenant ID: 16,1004004")
# ========================================================"

for arquivo in os.listdir(diretorio_pdf):
    file_path = os.path.join(diretorio_pdf, arquivo)
    try:
        if os.path.isfile(file_path): os.unlink(file_path)
    except Exception as e: 
        logger.warning(f"Erro ao limpar {file_path}: {e}")

try:
    logger.info("Iniciando processo de extração de certidões negativas")
    options = webdriver.ChromeOptions()
    prefs = {
    "plugins.always_open_pdf_externally": True,  # Pula a tela preta e baixa direto
    "download.default_directory": diretorio_pdf,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--mute-audio')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--force-device-scale-factor=1")
    
    logger.info("Buscando lista de CNPJs do banco de dados")
    cnpjFilial = getDb.resultado()
    logger.info(f"Total de CNPJs a processar: {len(cnpjFilial)}")

    for idx, cnpj in enumerate(cnpjFilial, 1):
        cnpj_final = cnpj[0] if isinstance(cnpj, tuple) else cnpj
        logger.info(f"[{idx}/{len(cnpjFilial)}] Processando CNPJ: {cnpj_final}")
        logger.info("=" * 70)
        
        try:
            driver = webdriver.Chrome(options=options)
            logger.debug(f"ChromeDriver iniciado para CNPJ {cnpj_final}")
            
            driver.get(url)
            logger.debug(f"Acessando URL: {url}")
            driver.maximize_window()

            tipoDoc = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'cnpj')))
            tipoDoc.click()
            logger.debug(f"Campo CNPJ clicado")

            numDoc = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'numeroDocumento')))

            # Injeção via JavaScript
            driver.execute_script("arguments[0].value = arguments[1];", numDoc, cnpj_final)
            logger.debug(f"CNPJ {cnpj_final} inserido no formulário")

            btOk = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'botaoSubmit')))
            btOk.click()
            logger.debug(f"Botão submit clicado para CNPJ {cnpj_final}")

            sleep(5)

            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="form"]/div/div[2]/span')))
                logger.debug(f"Página de resultado carregada para CNPJ {cnpj_final}")

                emitir_nova = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/div/div[6]/ul/li[2]/a')))
                emitir_nova.click()
                logger.debug(f"Link 'Emitir nova' clicado para CNPJ {cnpj_final}")

                sleep(50)

                caminho_destino = os.path.join(pasta_final_pdf, f"{cnpj_final}.pdf")
                download_sucesso = False

                # Espera o arquivo aparecer na pasta_download
                for i in range(1000):
                    arquivos = os.listdir(diretorio_pdf)

                    pdfs = [f for f in arquivos if f.endswith('.pdf') and not f.endswith('.crdownload')]
                    
                    if pdfs:
                        arquivo_origem = os.path.join(diretorio_pdf, pdfs[0])
 
                        shutil.move(arquivo_origem, caminho_destino)
                        
                        logger.info(f"Arquivo movido e renomeado para: {caminho_destino}")
                        download_sucesso = True
                        break
                    sleep(1)
                

                if os.path.exists(caminho_destino):
                    logger.info(f"✓ PDF salvo com sucesso para CNPJ {cnpj_final}")
                    
                    # ============================================================
                    # PASSO 1: PDF → JSON (salva arquivo em disco)
                    # ============================================================
                    logger.info(f"[PASSO 1] Extraindo dados do PDF para JSON...")
                    certidao = getInfosPdf.extrair_e_salvar_json(caminho_destino, cnpj_final)
                    
                    if certidao:
                        # ============================================================
                        # PASSO 2: Verifica arquivo JSON criado
                        # ============================================================
                        json_dir = r"C:\certidao_negativa\json"
                        caminho_json = os.path.join(json_dir, f"{cnpj_final}.json")
                        logger.info(f"[PASSO 2] Verificando arquivo JSON criado...")
                        
                        if os.path.exists(caminho_json):
                            try:
                                logger.info(f"  ✓ JSON criado em: {caminho_json}")
                                
                                # ============================================================
                                # PASSO 3: Envia o ARQUIVO JSON para a API
                                # ============================================================
                                # IMPORTANTE: A instância 'api_client' é REUTILIZADA!
                                # - Ela foi criada UMA VEZ no início do script
                                # - Agora está sendo usada para enviar o JSON deste CNPJ
                                # - No próximo loop, ela enviará um JSON diferente
                                # ============================================================
                                logger.info(f"[PASSO 3] Enviando arquivo JSON para API...")
                                logger.info(f"  Arquivo: {caminho_json}")
                                logger.info(f"  Endpoint: http://10.192.0.193:8885/rest/BFFS01FF/")
                                
                                resposta_api = api_client.enviar_json_arquivo(caminho_json)
                                logger.info(f"✓ JSON enviado com sucesso!")
                                logger.debug(f"  Resposta: {resposta_api}")
                                
                            except Exception as e:
                                logger.error(f"✗ Erro ao enviar JSON para API: {e}")
                        else:
                            logger.warning(f"✗ Arquivo JSON não foi criado: {caminho_json}")
                    else:
                        logger.warning(f"✗ Falha ao extrair dados do PDF para CNPJ {cnpj_final}")
                    
                    driver.close()
                    logger.info("=" * 70)
                else:
                    logger.warning(f"✗ Erro ao salvar o PDF para CNPJ {cnpj_final}")
                    driver.save_screenshot(f'print/erro_{cnpj_final}.png')
                    driver.close()

            except Exception as e:
                driver.save_screenshot(f'print/erro_{cnpj_final}.png')
                logger.error(f"Erro ao processar CNPJ {cnpj_final}: {str(e)}")
                driver.close()
                continue
                
        except Exception as e:
            logger.error(f"Erro crítico ao processar CNPJ {cnpj_final}: {str(e)}")
            continue

    logger.info("Processo de extração finalizado")
    
except Exception as e:
    logger.critical(f"Erro crítico na execução principal: {str(e)}")
    raise
