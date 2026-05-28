from abc import ABC, abstractmethod
from src.domain.models import Client, Event

class ClientRepository(ABC):
    @abstractmethod
    def save(self,client: Client) -> Client:
        pass

    @abstractmethod
    def update(self,id: int, data: dict) -> Client:
        pass

    @abstractmethod
    def get_by_email(self,cliente_email: str)-> Client:
        pass

class EventRepository(ABC):
    @abstractmethod
    def save_event(self, event: Event) -> None:
        pass
    @abstractmethod
    def event_processed(self, event_id: str) -> bool:
        pass

class PipefyClientInterface(ABC):
    @abstractmethod
    def create_card(self,client: Client, pipe_id: int) -> None:
        pass
    @abstractmethod
    def update_card_field(self, card_id: str, field_id: str, new_value: str) -> None:
        pass