import httpx
import asyncio
from typing import Optional
from models import CertidaoNegativa
from logger import setup_logger
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis do .env

logger = setup_logger(__name__)


class APIClient:
    """Cliente para enviar dados de Certidão Negativa para API"""
    
    def __init__(
        self,
        base_url: str = "http://10.192.0.193:8885/rest/BFFS01FF/",
        username: str = os.getenv("username"),
        password: str = os.getenv("password"),
        tenant_id: str = os.getenv("tenant_id"),
        timeout: int = 30
    ):
        """
        Inicializa o cliente da API
        
        Args:
            base_url: URL base da API
            username: Usuário para autenticação
            password: Senha para autenticação
            tenant_id: ID do tenant
            timeout: Timeout em segundos para requisições
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self.timeout = timeout
        
        logger.debug(f"APIClient inicializado para {base_url}")
    
    def _get_headers(self) -> dict:
        """Retorna headers padrão para requisições"""
        return {
            "Content-Type": "application/json",
            "tenantId": self.tenant_id
        }
    
    def enviar_certidao_sync(
        self,
        certidao: CertidaoNegativa,
        retry: int = 3
    ) -> dict:
        """
        Envia dados da certidão de forma síncrona (bloqueante)
        
        Args:
            certidao: Objeto CertidaoNegativa com os dados
            retry: Número de tentativas em caso de erro
            
        Returns:
            dict: Resposta da API
            
        Raises:
            Exception: Se falhar após todas as tentativas
        """
        logger.info(f"Enviando certidão para API: {certidao}")
        
        for tentativa in range(1, retry + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        self.base_url,
                        json=certidao.to_dict(),
                        headers=self._get_headers(),
                        auth=(self.username, self.password)
                    )
                    
                    logger.debug(f"Status Code: {response.status_code}")
                    
                    # Verifica se a resposta foi bem-sucedida
                    if response.status_code in [200, 201]:
                        logger.info(f"✓ Certidão enviada com sucesso: {certidao.numero_doc}")
                        return response.json()
                    else:
                        logger.warning(
                            f"Resposta inesperada (tentativa {tentativa}/{retry}): "
                            f"Status {response.status_code} - {response.text}"
                        )
                        
                        # Se for a última tentativa, lança exceção
                        if tentativa == retry:
                            logger.error(f"Falha ao enviar certidão após {retry} tentativas")
                            raise Exception(f"API retornou status {response.status_code}")
                        
                        # Aguarda antes de tentar novamente
                        asyncio.run(asyncio.sleep(2 ** tentativa))  # Backoff exponencial
                        
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão (tentativa {tentativa}/{retry}): {e}")
                
                if tentativa == retry:
                    raise
                asyncio.run(asyncio.sleep(2 ** tentativa))
            
            except Exception as e:
                logger.error(f"Erro inesperado (tentativa {tentativa}/{retry}): {e}")
                
                if tentativa == retry:
                    raise
                asyncio.run(asyncio.sleep(2 ** tentativa))
    
    async def enviar_certidao_async(
        self,
        certidao: CertidaoNegativa,
        retry: int = 3
    ) -> dict:
        """
        Envia dados da certidão de forma assíncrona (não-bloqueante)
        
        Args:
            certidao: Objeto CertidaoNegativa com os dados
            retry: Número de tentativas em caso de erro
            
        Returns:
            dict: Resposta da API
            
        Raises:
            Exception: Se falhar após todas as tentativas
        """
        logger.info(f"Enviando certidão para API (async): {certidao}")
        
        for tentativa in range(1, retry + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.base_url,
                        json=certidao.to_dict(),
                        headers=self._get_headers(),
                        auth=(self.username, self.password)
                    )
                    
                    logger.debug(f"Status Code: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✓ Certidão enviada com sucesso: {certidao.numero_doc}")
                        return response.json()
                    else:
                        logger.warning(
                            f"Resposta inesperada (tentativa {tentativa}/{retry}): "
                            f"Status {response.status_code} - {response.text}"
                        )
                        
                        if tentativa == retry:
                            logger.error(f"Falha ao enviar certidão após {retry} tentativas")
                            raise Exception(f"API retornou status {response.status_code}")
                        
                        await asyncio.sleep(2 ** tentativa)  # Backoff exponencial
                        
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão (tentativa {tentativa}/{retry}): {e}")
                
                if tentativa == retry:
                    raise
                await asyncio.sleep(2 ** tentativa)
            
            except Exception as e:
                logger.error(f"Erro inesperado (tentativa {tentativa}/{retry}): {e}")
                
                if tentativa == retry:
                    raise
                await asyncio.sleep(2 ** tentativa)
    
    def enviar_json_arquivo(
        self,
        caminho_json: str,
        retry: int = 3
    ) -> dict:
        """
        Envia um arquivo JSON salvo em disco para a API
        
        Args:
            caminho_json: Caminho do arquivo JSON
            retry: Número de tentativas em caso de erro
            
        Returns:
            dict: Resposta da API
            
        Raises:
            Exception: Se falhar após todas as tentativas
        """
        import json
        
        logger.info(f"Carregando JSON do arquivo: {caminho_json}")
        
        try:
            # Ler o arquivo JSON
            with open(caminho_json, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
            
            logger.debug(f"JSON carregado: {dados_json}")
            
            # Enviar para API
            logger.info(f"Enviando JSON para API: {caminho_json}")
            
            for tentativa in range(1, retry + 1):
                try:
                    with httpx.Client(timeout=self.timeout) as client:
                        response = client.post(
                            self.base_url,
                            json=dados_json,  # Envia o JSON diretamente
                            headers=self._get_headers(),
                            auth=(self.username, self.password)
                        )
                        
                        logger.debug(f"Status Code: {response.status_code}")
                        
                        if response.status_code in [200, 201]:
                            logger.info(f"✓ JSON enviado com sucesso para API")
                            return response.json()
                        else:
                            logger.warning(
                                f"Resposta inesperada (tentativa {tentativa}/{retry}): "
                                f"Status {response.status_code} - {response.text}"
                            )
                            
                            if tentativa == retry:
                                logger.error(f"Falha ao enviar JSON após {retry} tentativas")
                                raise Exception(f"API retornou status {response.status_code}")
                            
                            asyncio.run(asyncio.sleep(2 ** tentativa))
                            
                except httpx.RequestError as e:
                    logger.error(f"Erro de conexão (tentativa {tentativa}/{retry}): {e}")
                    
                    if tentativa == retry:
                        raise
                    asyncio.run(asyncio.sleep(2 ** tentativa))
                
                except Exception as e:
                    logger.error(f"Erro inesperado (tentativa {tentativa}/{retry}): {e}")
                    
                    if tentativa == retry:
                        raise
                    asyncio.run(asyncio.sleep(2 ** tentativa))
                    
        except FileNotFoundError:
            logger.error(f"Arquivo JSON não encontrado: {caminho_json}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON: {caminho_json}")
            raise
    
    async def enviar_multiplas_certidoes(
        self,
        certidoes: list[CertidaoNegativa]
    ) -> dict:
        """
        Envia múltiplas certidões de forma paralela (assíncrona)
        
        Args:
            certidoes: Lista de objetos CertidaoNegativa
            
        Returns:
            dict: Dicionário com status de cada certidão
        """
        logger.info(f"Enviando {len(certidoes)} certidões para API")
        
        tarefas = [
            self.enviar_certidao_async(certidao) 
            for certidao in certidoes
        ]
        
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)
        
        resultado_final = {
            "sucesso": 0,
            "erros": 0,
            "detalhes": []
        }
        
        for certidao, resultado in zip(certidoes, resultados):
            if isinstance(resultado, Exception):
                resultado_final["erros"] += 1
                resultado_final["detalhes"].append({
                    "numero_doc": certidao.numero_doc,
                    "status": "erro",
                    "mensagem": str(resultado)
                })
                logger.error(f"Erro ao enviar {certidao.numero_doc}: {resultado}")
            else:
                resultado_final["sucesso"] += 1
                resultado_final["detalhes"].append({
                    "numero_doc": certidao.numero_doc,
                    "status": "sucesso",
                    "resposta": resultado
                })
        
        logger.info(
            f"Envio em lote concluído: {resultado_final['sucesso']} sucesso, "
            f"{resultado_final['erros']} erros"
        )
        
        return resultado_final


# Exemplo de uso
if __name__ == "__main__":
    # Criar uma instância de CertidaoNegativa
    certidao = CertidaoNegativa(
        estado="MATO GROSSO",
        numero_doc="0062719864",
        data_emissao="30/04/2026",
        hora_emissao="11:49:54",
        validade="28/06/2026",
        autenticacao="TM9BLLB2BTTKU277"
    )
    
    # Enviar de forma síncrona
    cliente = APIClient()
    try:
        resposta = cliente.enviar_certidao_sync(certidao)
        print(f"Resposta: {resposta}")
    except Exception as e:
        print(f"Erro: {e}")
