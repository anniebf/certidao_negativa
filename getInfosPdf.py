import pdfplumber
import json
import re
from logger import setup_logger

logger = setup_logger(__name__)


def extrair_dados_especificos(texto):
    # Dicionário de padrões RegEx para encontrar as informações
    padroes = {
        "estado": r"ESTADO DE ([^\n\r]+)",
        "numero_doc": r"(?:CND|CPEND) Nº\s*(\d+)",
        "data_emissao": r"Data da emissão:\s*(\d{2}/\d{2}/\d{4})",
        "hora_emissao": r"Hora da emissão:\s*(\d{2}:\d{2}:\d{2})",
        "validade": r"Certidao válida até:\s*(\d{2}/\d{2}/\d{4})",
        "autenticacao": r"Número de Autenticação:\s*([A-Z0-9]+)"
    }
    
    dados = {}
    for chave, padrao in padroes.items():
        match = re.search(padrao, texto)
        if match:
            dados[chave] = match.group(1).strip()
        else:
            dados[chave] = None
            
    return dados

def extrair_e_salvar_json(caminho_pdf, nome_saida_json):
    texto_completo = ""
    try:
        logger.info(f"Iniciando extração de dados do PDF: {caminho_pdf}")
        # 1. Extração do texto
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                #print(texto_pagina)
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
                    
        
        # 2. Processamento dos dados
        dados_dict = extrair_dados_especificos(texto_completo)
        logger.debug(f"Dados extraídos: {dados_dict}")
        
        # 3. Salvamento do arquivo JSON
        # 'w' abre para escrita, encoding='utf-8' garante acentos corretos
        with open(fr'C:\certidao_negativa\json\{nome_saida_json}', 'w', encoding='utf-8') as f:
            json.dump(dados_dict, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Sucesso! Arquivo salvo em: {nome_saida_json}")
        return dados_dict

    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return None

if __name__ == "__main__":
    #caminho_arquivo_pdf = fr"C:\certidao_negativa\pdf\09181634000162.pdf"
    #nome_arquivo_json = "resultado_certidao.json" 
    
    extrair_e_salvar_json('', '')
    