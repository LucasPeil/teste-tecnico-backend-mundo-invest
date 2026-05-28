from src.domain.models import Client
from src.domain.interfaces import PipefyClientInterface
from typing import Optional
import json
class PipefyClient(PipefyClientInterface):
   
    def create_card(self, client: Client, pipe_id: int,) -> None:
        """Simulação de criação de um card no Pipefy com os dados do cliente."""
        mutation=f"""
        mutation{{
            createCard(input:{{
                pipe_id: {pipe_id},
                title: "{client.nome}",
                fields_attributes:[
                    {{field_id: "cliente_nome", field_value: "{client.nome}"}},
                    {{field_id: "cliente_email", field_value: "{client.email}"}},
                    {{field_id: "tipo_solicitacao", field_value: "{client.tipo_solicitacao}"}},
                    {{field_id: "valor_patrimonio", field_value: {client.valor_patrimonio}}},
                    {{field_id: "prioridade", field_value: "{client.prioridade}"}} 
                ]
            }}){{
                card {{
                title
                }}
          }}
        }}
        """
        payload = {
            "query": mutation
        }
        print(f"[PIPEFY MOCK] Enviando CreateCard:\n{mutation.strip()}")
     
    
    def update_card_field(self, card_id: str, field_id: str, new_value: str) -> None:
        """Simulação de atualização de um campo no Pipefy com os dados do cliente."""
        mutation = f"""
        mutation{{
            updateCardField(input:{{
                card_id: {card_id},
                field_id: "{field_id}",
                new_value: "{new_value}"
            }}){{
                card{{
                    title
                }}
            }}
        }}
        """
        payload = {
            "query": mutation
        }
        print(f"[PIPEFY MOCK] Enviando UpdateCardField:\n{mutation.strip()}")
