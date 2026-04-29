from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import getDb
import shutil
import os
from time import sleep, time
from logger import setup_logger
import getInfosPdf

logger = setup_logger(__name__)

url = "https://www.sefaz.mt.gov.br/cnd/certidao/servlet/ServletRotdAberto?origem=60"
diretorio_pdf = fr"C:\certidao_negativa\download"
pasta_final_pdf = r"C:\certidao_negativa\pdf"

for arquivo in os.listdir(diretorio_pdf):
    file_path = os.path.join(diretorio_pdf, arquivo)
    try:
        if os.path.isfile(file_path): os.unlink(file_path)
    except Exception as e: print(f"Erro ao limpar: {e}")

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

                sleep(100)

                caminho_destino = os.path.join(pasta_final_pdf, f"{cnpj_final}.pdf")
                download_sucesso = False

                # Espera o arquivo aparecer na pasta_download
                for i in range(100):
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
                    getInfosPdf.extrair_e_salvar_json(caminho_destino, cnpj_final)
                    driver.close()
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
