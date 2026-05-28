from src.domain.models import Client, Event
from src.domain.interfaces import ClientRepository, EventRepository, PipefyClientInterface
from src.application.dtos import UseCaseResponse

class CreateClientUseCase:
    def __init__(self, client_repo: ClientRepository, pipefy_client: PipefyClientInterface):
        self.client_repo = client_repo
        self.pipefy_client = pipefy_client

    def execute(self, cliente_nome:str, cliente_email:str, tipo_solicitacao:str, valor_patrimonio:float) -> UseCaseResponse:
        """
        Cria um novo cliente no banco de dados e gera um card no pipefy.
        
        Se o cliente já existir, retorna uma mensagem de erro.
        """
       
        client_exists = self.client_repo.get_by_email(cliente_email)
        if client_exists:
            return UseCaseResponse(
                message=f"Já existe um cliente cadastrado com o email {cliente_email}",
                status_code=409,  
                response=None
            )

        client = Client(
            nome=cliente_nome,
            email=cliente_email,
            tipo_solicitacao=tipo_solicitacao,
            valor_patrimonio=valor_patrimonio
        )
        #Persistência local
        saved_client = self.client_repo.save(client)
        
        #Mapeamento Pipefy
        self.pipefy_client.create_card(client, pipe_id=123)  # Pipe ID fixo para exemplo
        print("Cliente criado e card no Pipefy gerado com sucesso!")
        return UseCaseResponse(
            message='Cliente criado com sucesso',
            status_code=201,
            response=saved_client
        )

class ProcessarWebhookUseCase:
    def __init__(self, client_repo: ClientRepository, event_repo: EventRepository, pipefy_client: PipefyClientInterface):
        self.client_repo = client_repo
        self.event_repo = event_repo
        self.pipefy_client = pipefy_client

    def execute(self, event_id:str, card_id:str, cliente_email:str, timestamp:str) -> UseCaseResponse:
        """
        Processa um evento recebido do Pipefy.

        Se o evento já foi processado, retorna uma mensagem de erro.
        Caso contrário, registra o evento, atualiza o card do pipefy com a prioridade e o status do cliente 
        e atualiza o registro do cliente no banco de dados.
        """
        event = Event(
            event_id=event_id,
            card_id=card_id,
            cliente_email=cliente_email,
            timestamp=timestamp
        )

        if self.event_repo.event_processed(event_id = event_id):
             return UseCaseResponse(message="Evento já processado", status_code=400, response=None)
        
        #Registrar o evento
        self.event_repo.save_event(event)
        
        db_client = self.client_repo.get_by_email( cliente_email = cliente_email)
        
        if not db_client:
            return UseCaseResponse(message="Cliente não encontrado", status_code=404, response=None)    
        
        priority = "prioridade_alta" if db_client.valor_patrimonio >= 200000 else "prioridade_normal"

        # Atualizar o campo de prioridade no card do Pipefy
        self.pipefy_client.update_card_field(card_id=card_id, field_id="prioridade", new_value=priority)
        print(f"Campo 'prioridade' atualizado para {priority} no card {card_id}.")
        
        # Atualizar o campo de status no card do Pipefy
        self.pipefy_client.update_card_field(card_id=card_id, field_id="status", new_value="Processado") 
        print(f"Campo 'status' atualizado para 'Processado' no card {card_id}.")

        # Atualizar o status do cliente no banco de dados
        updated_client = self.client_repo.update(id=db_client.id, data={"prioridade": priority, "status": "Processado"})
        if not updated_client:
            return UseCaseResponse(message="Cliente não encontrado. Não foi possível update.", status_code=404, response=None)

        print(f"Status do cliente {db_client.nome} atualizado para 'Processado' com prioridade {priority} no banco de dados.")

        return UseCaseResponse(
            message='Webhook processado com sucesso',
            status_code=200,
            response={
                'cliente': updated_client.nome,
                'prioridade': updated_client.prioridade,
                'status': updated_client.status
            }
        )
       






       