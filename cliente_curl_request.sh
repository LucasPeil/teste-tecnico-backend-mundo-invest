#!/bin/bash
# Exemplo de requisições curl para os endpoints da API

HOST="http://127.0.0.1:8000"

# Criar cliente
# POST /clientes
curl -X POST -i "$HOST/clientes" \
  -H "Content-Type: application/json" \
  -d '{"cliente_nome":"Marcio Oliveira","cliente_email":"marcio.oliveira@example.com","tipo_solicitacao":"Atualizacao cadastral","valor_patrimonio":200000}'
