from sqlalchemy import Column, Integer, String, Float
from src.infrastructure.database import Base

class ClientORM(Base):
    __tablename__ = 'clientes'

    id=Column(Integer, primary_key=True, index=True)
    nome=Column(String, nullable=False)
    email=Column(String,unique=True, nullable=False, index=True)
    tipo_solicitacao=Column(String,nullable=False)
    valor_patrimonio = Column(Float, nullable=False)
    status = Column(String, default="Aguardando Análise")
    prioridade = Column(String, nullable=True)

class EventORM(Base):
    __tablename__ = 'eventos'

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String,unique=True, nullable=False, index=True)
    card_id = Column(String, nullable=False, index=True)
    cliente_email = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)