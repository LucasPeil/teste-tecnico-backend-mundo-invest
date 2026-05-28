# Projeto de Integração Pipefy

Este projeto é uma API desenvolvida com **FastAPI** para gerenciamento de clientes e integração via webhooks com o Pipefy. A aplicação possui endpoints para criação de novos clientes e processamento de webhooks disparados pelo Pipefy (ex: criação/atualização de cards).

## 1. Executando o Projeto Localmente

### Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Compose instalados.
- Python 3.10+ .

### Passo a passo para execução

1. **Configurar as variáveis de ambiente (.env):**
   Na raiz do projeto, crie um arquivo chamado `.env` e adicione as seguintes variáveis (utilizadas na conexão com o banco de dados principal e de testes):
   ```env
   POSTGRES_USER=usuario_do_banco_postgres
   POSTGRES_PASSWORD=senha_do_banco_postgres
   POSTGRES_DB=nome_do_banco_postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432

   POSTGRES_USER_TEST=usuario_do_banco_postgres
   POSTGRES_PASSWORD_TEST=senha_do_banco_postgres
   POSTGRES_DB_TEST=nome_do_banco_postgres
   POSTGRES_HOST_TEST=localhost
   POSTGRES_PORT_TEST=5433
   ```

2. **Subir os serviços de banco de dados:**
   O projeto utiliza o PostgreSQL como banco de dados. Inicie os containers de desenvolvimento e de testes executando:
   ```bash
   docker-compose up -d
   ```
   *Isso disponibilizará o banco de dados da aplicação na porta 5432 e o banco de testes na porta 5433.*

3. **Configurar o ambiente virtual e dependências:**
   No diretório raiz do projeto, crie e ative um ambiente virtual:
   ```bash
   # Criar o ambiente virtual (venv)
   python -m venv .venv
   
   # Ativar o venv (No Windows)
   .venv\Scripts\activate
   # (No Linux/Mac, utilize: source .venv/bin/activate)

   # Instalar dependências
   pip install -r requirements.txt
   ```

4. **Executar a API:**
   Com o ambiente virtual ativado, inicie o servidor:
   ```bash
    uvicorn src.presentation.api:app --reload --host 0.0.0.0 --port 8000
   ```
   *A API estará disponível em `http://127.0.0.1:8000`.*

### Executando os Testes

Para rodar os testes (garanta que os bancos de dados do Docker estão em execução):
```bash
python -m pytest src/tests/test_api.py
```

---

## 2. Exemplos de Requisição (Endpoints)

Abaixo estão os exemplos de como fazer requisições para a API utilizando o comando `curl`. Os mesmos exemplos podem ser encontrados nos arquivos `.sh` do repositório.

### Endpoint 1: Criar Cliente (`POST /clientes`)
Este endpoint recebe os dados de um cliente, salva no banco de dados e cria um card no Pipefy através da mutation `createCard`.

```bash
curl -X POST -i "http://127.0.0.1:8000/clientes" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Marcio Oliveira",
    "cliente_email": "marcio.oliveira@example.com",
    "tipo_solicitacao": "Atualizacao cadastral",
    "valor_patrimonio": 200000
  }'
```

### Endpoint 2: Processar Webhook Pipefy (`POST /webhooks/pipefy/card-updated`)
Este endpoint simula o recebimento de eventos disparados pelo Pipefy (por exemplo, alterações em um card dentro do Pipefy).

```bash
curl -X POST -i "http://127.0.0.1:8000/webhooks/pipefy/card-updated" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_1234567",
    "card_id": "card_1234567",
    "cliente_email": "marcio.oliveira@example.com",
    "timestamp": "2026-03-26T12:00:00Z"
  }'
```

---

## 3. Visão de Produção (AWS)

Para escalar essa arquitetura de processamento de webhooks e banco de dados em um ambiente de produção AWS, a seguinte arquitetura seria recomendada:

- **Amazon API Gateway:** Atuaria como a porta de entrada segura para a API. O API Gateway é um serviço totalmente gerenciado que fornece controle de tráfego, autenticação (Amazon Cognito) e proteção contra picos abruptos de requisições disparadas pelo Pipefy.
- **AWS Lambda:** Em vez de manter um servidor rodando ininterruptamente (como o Uvicorn em uma instância EC2), os endpoints podem ser processados por funções Lambda. Como a arquitetura é *serverless*, ela escala vertical e automaticamente (alocando recursos computacionais) de forma praticamente imediata quando recebe muitos webhooks, cobrando apenas pelo tempo de execução.
- **Amazon SQS (Serviço de Fila de Mensagens - Recomendado):** Para webhooks, a melhor prática é **desacoplar** o recebimento do evento do seu processamento. O API Gateway poderia encaminhar o evento do Pipefy diretamente para uma fila do SQS. Uma função Lambda então consumiria as mensagens da fila em um ritmo que o banco de dados suporte. Isso previne perda de eventos e gargalos/sobrecarga no banco de dados.
- **Banco de Dados (Amazon RDS ou DynamoDB):** 
  - **Amazon RDS (PostgreSQL):** Como a aplicação foi desenvolvida utilizando PostgreSQL e a modelagem é relacional (com o SQLAlchemy), utilizar o RDS com PostgreSQL configurado como *Multi-AZ* seria a transição mais natural. Isso confere alta disponibilidade (failover automático) e backups automatizados. Se a leitura for um gargalo, pode-se utilizar *Read Replicas*. Um dos pontos negativos é que a conexão com o Lambda requer configurações adicionais se comparado com o DynamoDB.
  - **Amazon DynamoDB (NoSQL):** Caso o requisito fosse um armazenamento extremamente rápido para alto volume de dados (onde eventos do webhook pudessem escalar para milhões por segundo), e não haja necessidade de querys com joins complexas, migrar os repositórios para o DynamoDB seria interessante, pois ele integra-se mais facilmente e de forma otimizada com o restante do ecossistema serverless.

**Resumo do Fluxo na AWS:**
`Pipefy (Webhook)` ➜ `API Gateway` ➜ `SQS (Fila)` ➜ `Lambda (Processador)` ➜ `Amazon RDS (PostgreSQL)`
