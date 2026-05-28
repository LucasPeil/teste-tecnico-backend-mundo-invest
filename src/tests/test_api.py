import pytest
from fastapi.testclient import TestClient
from src.presentation.api import app, get_db
from src.infrastructure.repositores import SqlClientRepository, SqlEventRepository
from test_database import  engine, TestingSessionLocal
from src.infrastructure.orm_models import Base
client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    # Cria todas as tabelas no banco de teste antes do teste rodar
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Destrói todas as tabelas no fim do teste.
        Base.metadata.drop_all(bind=engine)

# Fazendo o override do banco de desenvolvimento para o banco de teste
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()



## Testes de Integração para a API
def test_create_client_valid_payload(client):
    payload = {
        "cliente_nome": "Joao Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000
    }
    response = client.post("/clientes", json=payload)
    
    assert response.status_code == 201
    assert response.json()["status_code"] == 201
    assert response.json()["response"]["status"] == "Aguardando Análise"


def test_process_webhook_high_priority(client):
    client_payload = {
        "cliente_nome": "Maria", 
        "cliente_email": "maria@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 200000
    }
    webhook_payload = {
        "event_id": "evt_123", 
        "card_id": "card_456",
        "cliente_email": "maria@example.com", 
        "timestamp": "2026-05-18T12:00:00Z"
    }
    
    client.post("/clientes", json=client_payload)

    response = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    
    assert response.status_code == 200
    assert response.json()["response"]["prioridade"] == "prioridade_alta"
    assert response.json()["response"]["status"] == "Processado"


def test_process_webhook_normal_priority(client):
    client_payload = {
        "cliente_nome": "Pedro", 
        "cliente_email": "pedro@example.com",
        "tipo_solicitacao": "Atualização cadastral", 
        "valor_patrimonio": 50000
    }

    webhook_payload = {
        "event_id": "evt_234", 
        "card_id": "card_567",
        "cliente_email": "pedro@example.com", 
        "timestamp": "2026-04-18T12:00:00Z"
    }

    client.post("/clientes", json=client_payload)
    
    response = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    
    assert response.status_code == 200
    assert response.json()["response"]["prioridade"] == "prioridade_normal"
    assert response.json()["response"]["status"] == "Processado"
def test_block_processing_duplicate_event_id(client):
    client_payload = {
        "cliente_nome": "Carlos", 
        "cliente_email": "carlos@example.com",
        "tipo_solicitacao": "Atualização cadastral", 
        "valor_patrimonio": 100000
    }
    client.post("/clientes", json=client_payload)
    webhook_payload = {
        "event_id": "evt_345", 
        "card_id": "card_678",
        "cliente_email": "carlos@example.com", 
        "timestamp": "2026-07-18T12:00:00Z"
    }

    # Primeira chamada: sucesso 
    resp1 = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert resp1.status_code == 200
    assert resp1.json()["response"]["prioridade"] == "prioridade_normal"

    # Segunda chamada com o mesmo event_id: deve ignorar
    resp2 = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Evento já processado"