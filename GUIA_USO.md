# Guia de Uso - Sistema de Certidão Negativa

## Estrutura do Projeto

### Arquivos Principais:

1. **`models.py`** - Define a classe `CertidaoNegativa` usando Pydantic
2. **`api_client.py`** - Cliente para enviar dados para a API
3. **`getInfosPdf.py`** - Extrai dados dos PDFs
4. **`main.py`** - Orquestrador principal (Selenium + Extração + Envio API)
5. **`logger.py`** - Sistema centralizado de logging
6. **`getDb.py`** - Conexão com banco Oracle
7. **`postJson.py`** - Exemplos de uso dos envios

---

## Como Usar

### 1. Criar uma Certidão Negativa

```python
from models import CertidaoNegativa

certidao = CertidaoNegativa(
    estado="MATO GROSSO",
    numero_doc="0062719864",
    data_emissao="30/04/2026",
    hora_emissao="11:49:54",
    validade="28/06/2026",
    autenticacao="TM9BLLB2BTTKU277",
    cnpj="12.345.678/0001-90"  # Opcional
)

print(certidao)
# Saída: CertidaoNegativa(doc=0062719864, estado=MATO GROSSO, valida até 28/06/2026)
```

### 2. Enviar para API - Forma Síncrona (Bloqueante)

```python
from models import CertidaoNegativa
from api_client import APIClient

certidao = CertidaoNegativa(
    estado="MATO GROSSO",
    numero_doc="0062719864",
    data_emissao="30/04/2026",
    hora_emissao="11:49:54",
    validade="28/06/2026",
    autenticacao="TM9BLLB2BTTKU277"
)

cliente = APIClient()
resposta = cliente.enviar_certidao_sync(certidao)
print(resposta)
```

### 3. Enviar para API - Forma Assíncrona (Não-bloqueante)

```python
import asyncio
from models import CertidaoNegativa
from api_client import APIClient

async def enviar():
    certidao = CertidaoNegativa(
        estado="MATO GROSSO",
        numero_doc="0062719864",
        data_emissao="30/04/2026",
        hora_emissao="11:49:54",
        validade="28/06/2026",
        autenticacao="TM9BLLB2BTTKU277"
    )
    
    cliente = APIClient()
    resposta = await cliente.enviar_certidao_async(certidao)
    print(resposta)

asyncio.run(enviar())
```

### 4. Enviar Múltiplas Certidões em Paralelo

```python
import asyncio
from models import CertidaoNegativa
from api_client import APIClient

async def enviar_lote():
    certidoes = [
        CertidaoNegativa(
            estado="MATO GROSSO",
            numero_doc="0062719864",
            data_emissao="30/04/2026",
            hora_emissao="11:49:54",
            validade="28/06/2026",
            autenticacao="TM9BLLB2BTTKU277"
        ),
        CertidaoNegativa(
            estado="MATO GROSSO",
            numero_doc="0062719865",
            data_emissao="01/05/2026",
            hora_emissao="12:00:00",
            validade="29/06/2026",
            autenticacao="TM9BLLB2BTTKU278"
        ),
    ]
    
    cliente = APIClient()
    resultado = await cliente.enviar_multiplas_certidoes(certidoes)
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Erros: {resultado['erros']}")
    print(f"Detalhes: {resultado['detalhes']}")

asyncio.run(enviar_lote())
```

### 5. Extrair Dados do PDF e Enviar

```python
from getInfosPdf import extrair_e_salvar_json
from api_client import APIClient

# Extrair dados do PDF (retorna objeto CertidaoNegativa)
certidao = extrair_e_salvar_json(
    caminho_pdf="C:/certidao_negativa/pdf/12345678000190.pdf",
    cnpj="12345678000190"
)

if certidao:
    # Enviar para API
    cliente = APIClient()
    resposta = cliente.enviar_certidao_sync(certidao)
    print(resposta)
```

---

## Fluxo Principal (main.py)

```
1. Conecta ao banco Oracle → Busca CNPJs
2. Para cada CNPJ:
   a. Abre Selenium e acessa o site da SEFAZ-MT
   b. Preenche formulário com o CNPJ
   c. Faz download do PDF
   d. Extrai dados do PDF (retorna CertidaoNegativa)
   e. Envia dados para API via HTTPClient
   f. Salva JSON com os dados extraídos
3. Registra tudo no arquivo de log
```

---

## Configuração da API

Se precisar mudar os dados de acesso da API, altere ao criar o cliente:

```python
cliente = APIClient(
    base_url="http://10.192.0.193:8885/rest/BFFS01FF/",
    username="Admin",
    password="Suporte@2026",
    tenant_id="16,1004004",
    timeout=30
)
```

---

## Logging

Todos os eventos são registrados em:
- **Arquivo**: `logs/app_YYYYMMDD_HHMMSS.log`
- **Console**: Mensagens de INFO e acima

Níveis de log usados:
- **DEBUG**: Detalhes técnicos (raramente necessário)
- **INFO**: Eventos importantes
- **WARNING**: Situações inesperadas mas esperadas
- **ERROR**: Erros sem parar a execução
- **CRITICAL**: Erros graves que param tudo

---

## Tratamento de Erros

A API cliente implementa:
- ✓ Tentativas automáticas (retry) com backoff exponencial
- ✓ Timeout configurável
- ✓ Logs detalhados de cada tentativa
- ✓ Validação de campos obrigatórios

---

## Exemplo Completo

```python
from models import CertidaoNegativa
from api_client import APIClient
from logger import setup_logger

logger = setup_logger(__name__)

try:
    # Criar certidão
    certidao = CertidaoNegativa(
        estado="MATO GROSSO",
        numero_doc="0062719864",
        data_emissao="30/04/2026",
        hora_emissao="11:49:54",
        validade="28/06/2026",
        autenticacao="TM9BLLB2BTTKU277",
        cnpj="12.345.678/0001-90"
    )
    
    # Enviar
    cliente = APIClient()
    resposta = cliente.enviar_certidao_sync(certidao)
    
    logger.info(f"Sucesso! Resposta: {resposta}")
    
except Exception as e:
    logger.error(f"Falha na operação: {e}")
```

