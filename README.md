# Certidão Negativa - SEFAZ MT

> Automação para download e processamento de certidões negativas da SEFAZ-MT

**Projeto criado por:** hianny.urt

## 📋 Descrição

Este projeto automatiza o processo de:

1. **Download de Certidões Negativas** - Consulta a plataforma de certidões da SEFAZ-MT para múltiplos CNPJs
2. **Extração de Dados** - Extrai informações estruturadas dos PDFs gerados
3. **Armazenamento** - Salva os dados em formato JSON para processamento no protheus

O sistema busca uma lista de CNPJs de um banco de dados, acessa o site da SEFAZ-MT automaticamente via Selenium, baixa os PDFs das certidões e extrai as informações relevantes usando regex.

## 🚀 Requisitos

- Python 3.12.10
- Chrome/Chromium instalado (para Selenium)
- Acesso a banco de dados Oracle
- Variáveis de ambiente configuradas (.env)

## 📦 Instalação

### 1. Clonar ou baixar o projeto

```bash
cd c:\certidao_negativa
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Criar arquivo `.env` na raiz do projeto:

```
usernamedb=seu_usuario_oracle
password=sua_senha_oracle
dsn=seu_dsn_oracle
```

## 🔧 Uso

Execute o script principal:

```bash
python main.py
```

O sistema irá:
- Conectar ao banco de dados Oracle
- Buscar lista de CNPJs
- Para cada CNPJ:
  - Acessar o site da SEFAZ-MT
  - Preencher formulário com CNPJ
  - Baixar PDF da certidão
  - Extrair dados do PDF
  - Salvar JSON com informações extraídas

## 📁 Estrutura do Projeto

```
certidao_negativa/
├── main.py                 # Script principal de automação
├── getDb.py               # Módulo de conexão com banco de dados Oracle
├── getInfosPdf.py         # Módulo de extração de dados de PDF
├── logger.py              # Configuração de logging
├── requirements.txt       # Dependências do projeto
├── .env                   # Variáveis de ambiente (não versionado)
│
├── download/              # Pasta temporária de downloads
├── pdf/                   # PDFs finais das certidões
├── json/                  # JSONs com dados extraídos
└── logs/                  # Arquivos de log
```

## 📄 Módulos

### `main.py`
Script principal que:
- Configura opções do Chrome
- Itera sobre lista de CNPJs
- Automatiza acesso ao site da SEFAZ-MT
- Gerencia downloads e movimentação de arquivos
- Chama extração de dados dos PDFs

### `getDb.py`
Responsável por:
- Conectar ao banco de dados Oracle
- Executar query para buscar CNPJs
- Retornar lista de CNPJs para processamento

### `getInfosPdf.py`
Responsável por:
- Abrir e ler arquivos PDF
- Extrair dados específicos usando RegEx:
  - Estado
  - Número do documento (CND/CPEND)
  - Data de emissão
  - Hora de emissão
  - Validade da certidão
  - Número de autenticação
- Salvar dados em arquivo JSON

### `logger.py`
Sistema de logging que:
- Registra eventos em arquivo com rotação (5MB, até 5 backups)
- Exibe informações no console
- Inclui timestamp e informações de linha de código

## 📊 Dados Extraídos do PDF

Cada JSON gerado contém:

```json
{
  "estado": "MATO GROSSO",
  "numero_doc": "123456789",
  "data_emissao": "01/01/2024",
  "hora_emissao": "10:30:45",
  "validade": "31/12/2024",
  "autenticacao": "ABC123XYZ"
}
```

## 📝 Logs

Os logs são salvos automaticamente em `logs/app_YYYYMMDD_HHMMSS.log` com:
- Timestamp
- Nome do módulo
- Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Arquivo e linha de execução
- Mensagem descritiva

## ⚙️ Configuração de Variáveis de Ambiente

Criar arquivo `.env` com:

```
usernamedb=seu_usuario
password=sua_senha
dsn=seu_dsn_string
```

**Exemplo de DSN Oracle:**
```
dsn=usuario/senha@host:1521/service_name
```

## 🔍 Fluxo de Execução

```
1. Carregar CNPJs do banco de dados Oracle
2. Para cada CNPJ:
   ├─ Iniciar navegador Chrome
   ├─ Acessar SEFAZ-MT
   ├─ Preencher formulário
   ├─ Aguardar carregamento
   ├─ Clicar "Emitir Nova"
   ├─ Aguardar download
   ├─ Mover PDF para pasta final
   ├─ Extrair dados do PDF
   ├─ Salvar JSON
   └─ Fechar navegador
3. Finalizar processo
```

## 🐛 Troubleshooting

### Erro de conexão com Oracle
- Verificar credenciais no `.env`
- Verificar conectividade com servidor Oracle
- Consultar logs em `logs/`

### PDFs não baixam
- Verificar se Chrome está instalado
- Verificar permissões da pasta `download/`
- Aumentar tempo de espera em `sleep(50)`

### Dados não extraem corretamente
- Verificar se padrões RegEx correspondem ao PDF
- Verificar encoding UTF-8
- Consultar texto extraído nos logs de DEBUG

## 📦 Dependências Principais

- `selenium` - Automação do navegador
- `pdfplumber` - Leitura e extração de PDFs
- `oracledb` - Conexão com banco de dados Oracle
- `python-dotenv` - Gerenciamento de variáveis de ambiente

## 📜 Licença

Projeto interno - Boa Futuro

---

**Criado por:** hianny.urt  
**Última atualização:** 2024
