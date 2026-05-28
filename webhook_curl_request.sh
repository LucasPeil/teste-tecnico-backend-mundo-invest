#!/bin/bash
# Exemplo de requisições curl para os endpoints da API

HOST="http://127.0.0.1:8000"

# Processar webhook Pipefy
# POST /webhooks/pipefy/card-updated
curl -X POST "$HOST/webhooks/pipefy/card-updated" \
  -H "Content-Type: application/json" \
  -d '{"event_id":"evt_1234567","card_id":"card_1234567","cliente_email":"marcio.oliveira@example.com","timestamp":"2026-03-26T12:00:00Z"}'

