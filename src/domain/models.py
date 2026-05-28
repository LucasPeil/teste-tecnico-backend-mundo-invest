from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    nome: str
    email: str
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str = 'Aguardando Análise'
    prioridade: Optional[str] = None
    id: Optional[int] = None

@dataclass
class Event:
    event_id: str
    card_id: str
    cliente_email: str
    timestamp: str

    