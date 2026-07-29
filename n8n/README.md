# n8n

Workflows de automatizacion exportados.

## Webhooks disponibles

- POST /api/v1/automation/today/
- POST /api/v1/automation/upcoming/
- POST /api/v1/automation/events/
- POST /api/v1/automation/events/{uuid}/confirm/
- GET /api/v1/integrations/health/

## Autenticacion

Header: X-N8N-API-Key

## Eventos

Los webhooks hacia n8n usan HMAC-SHA256.
