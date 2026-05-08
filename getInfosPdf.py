import pdfplumber
import json
import re
from logger import setup_logger
from models import CertidaoNegativa

logger = setup_logger(__name__)


def extrair_dados_especificos(texto: str) -> dict:
    """
    Extrai dados específicos do PDF usando regex
    
    Args:
        texto: Texto completo extraído do PDF
        
    Returns:
        dict: Dicionário com os dados extraídos
    """
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
            logger.warning(f"Padrão '{chave}' não encontrado no PDF")
            
    return dados

def extrair_e_salvar_json(caminho_pdf: str, cnpj: str) -> CertidaoNegativa or None:
    """
    Extrai dados do PDF e salva como JSON, retornando objeto CertidaoNegativa
    
    Args:
        caminho_pdf: Caminho do arquivo PDF
        cnpj: CNPJ para salvar o arquivo JSON
        
    Returns:
        CertidaoNegativa: Objeto com os dados extraídos, ou None se erro
    """
    texto_completo = ""
    try:
        logger.info(f"Iniciando extração de dados do PDF: {caminho_pdf}")
        
        # 1. Extração do texto
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
                    
        
        # 2. Processamento dos dados
        dados_dict = extrair_dados_especificos(texto_completo)
        logger.debug(f"Dados extraídos: {dados_dict}")
        
        # Validar se todos os campos obrigatórios foram encontrados
        campos_obrigatorios = ["estado", "numero_doc", "data_emissao", "hora_emissao", "validade", "autenticacao"]
        campos_faltantes = [campo for campo in campos_obrigatorios if not dados_dict.get(campo)]
        
        if campos_faltantes:
            logger.error(f"Campos faltantes no PDF: {campos_faltantes}")
            return None
        
        # 3. Criar objeto CertidaoNegativa
        certidao = CertidaoNegativa(
            estado=dados_dict["estado"],
            numero_doc=dados_dict["numero_doc"],
            data_emissao=dados_dict["data_emissao"],
            hora_emissao=dados_dict["hora_emissao"],
            validade=dados_dict["validade"],
            autenticacao=dados_dict["autenticacao"],
            cnpj=cnpj
        )
        
        # 4. Salvar arquivo JSON
        import os
        json_dir = r"C:\certidao_negativa\json"
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
            
        nome_arquivo = f"{cnpj}.json"
        caminho_json = os.path.join(json_dir, nome_arquivo)
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(certidao.dict(), f, indent=4, ensure_ascii=False)
            
        logger.info(f"✓ Arquivo JSON salvo em: {caminho_json}")
        return certidao

    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return None

if __name__ == "__main__":
    #caminho_arquivo_pdf = fr"C:\certidao_negativa\pdf\09181634000162.pdf"
    #nome_arquivo_json = "resultado_certidao.json" 
    
    extrair_e_salvar_json('', '')
    