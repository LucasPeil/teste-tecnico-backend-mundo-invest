from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from src.application.use_cases import CreateClientUseCase, ProcessarWebhookUseCase
from src.infrastructure.repositores import SqlClientRepository, SqlEventRepository
from src.infrastructure.pipefy_service import PipefyClient
from src.infrastructure.database import session_local, engine
from src.infrastructure.orm_models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa ao iniciar a API
    Base.metadata.create_all(bind=engine)
    yield
    

app = FastAPI(
    title="API de Gerenciamento de Clientes e Integração com Pipefy",
    lifespan=lifespan
)

pipefy_client = PipefyClient()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# Schemas de Validação
class ClientRequest(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: float

class WebhookEventRequest(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: str

@app.post("/clientes", status_code=status.HTTP_201_CREATED)
def criar_cliente(payload: ClientRequest, db: Session = Depends(get_db)):

    client_repo = SqlClientRepository(db)
    use_case = CreateClientUseCase(client_repo, pipefy_client)
    result = use_case.execute(
        cliente_nome=payload.cliente_nome,
        cliente_email=payload.cliente_email,
        tipo_solicitacao=payload.tipo_solicitacao,
        valor_patrimonio=payload.valor_patrimonio
    )
    if result.status_code != 201:
        raise HTTPException(status_code=result.status_code, detail=result.message)
    return result


@app.post("/webhooks/pipefy/card-updated", status_code=status.HTTP_200_OK)
def processar_webhook(payload: WebhookEventRequest, db: Session = Depends(get_db)):

    client_repo = SqlClientRepository(db)
    event_repo = SqlEventRepository(db)
    use_case = ProcessarWebhookUseCase(client_repo, event_repo, pipefy_client)
    try:
        result = use_case.execute(
            event_id=payload.event_id,
            card_id=payload.card_id,
            cliente_email=payload.cliente_email,
            timestamp=payload.timestamp
        )
        if result.status_code != 200:
            raise HTTPException(status_code=result.status_code, detail=result.message)
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {e}")