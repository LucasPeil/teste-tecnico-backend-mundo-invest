from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.models import Client, Event
from src.domain.interfaces import ClientRepository, EventRepository
from src.infrastructure.orm_models import ClientORM, EventORM
from sqlalchemy.dialects.postgresql import insert
class SqlClientRepository(ClientRepository):
    def __init__(self,db: Session):
        self.db = db

    def save(self,client: Client) -> Client:
        """
        Cria um novo cliente no banco de dados.
        """
        client_orm = ClientORM(
            nome=client.nome,
            email=client.email,
            tipo_solicitacao=client.tipo_solicitacao,
            valor_patrimonio=client.valor_patrimonio
        )
        self.db.add(client_orm)
        self.db.commit()
        self.db.refresh(client_orm)

        client.id = client_orm.id

        return client

    def update(self, id: int, data: dict) -> Optional[Client]:
        """
        Atualiza um cliente no banco de dados.
        """
        client_orm = self.db.get(ClientORM, id)

        if not client_orm:
            return None

        for key, value in data.items():
            setattr(client_orm, key, value)

        self.db.commit()
        self.db.refresh(client_orm)
    
        return Client(
            id=client_orm.id,
            nome=client_orm.nome,
            email=client_orm.email,
            tipo_solicitacao=client_orm.tipo_solicitacao,
            valor_patrimonio=client_orm.valor_patrimonio,
            status=client_orm.status,
            prioridade=client_orm.prioridade
        )

    def get_by_email(self, cliente_email:str ) -> Optional[Client]:
        """
        Busca um cliente no banco de dados pelo email.
        """
        stmt = select(ClientORM).where(ClientORM.email == cliente_email)
        client = self.db.scalar(stmt)
        if not client:
            return None
        
        return Client(
            id=client.id,
            nome=client.nome,
            email=client.email,
            tipo_solicitacao=client.tipo_solicitacao,
            valor_patrimonio=client.valor_patrimonio,
            status=client.status,
            prioridade=client.prioridade
        )

class SqlEventRepository(EventRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save_event(self, event: Event) -> str:
        """
        Registra um evento no banco de dados.

        Utiliza uma operação de upsert para garantir a idempotência, evitando que o mesmo evento 
        seja processado múltiplas vezes em caso de reenvios/falhas na comunicação.
        """
        stmt = insert(EventORM).values(
            event_id= event.event_id,
            card_id = event.card_id,
            cliente_email = event.cliente_email,
            timestamp = event.timestamp
        )

        stmt = stmt.on_conflict_do_nothing(index_elements=['event_id'])

        self.db.execute(stmt)
        self.db.commit()
        return f"Evento {event.event_id} registrado com sucesso!"
    
    def event_processed(self, event_id: str) -> bool:
        """ Verifica se o evento com oevent_id já foi registrado no banco de dados, indicando que já foi processado."""
        
        stmt =  select(EventORM).where(EventORM.event_id == event_id)
        event = self.db.scalar(stmt)
        return event is not None
    
