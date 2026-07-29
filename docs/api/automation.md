# API de Automatización (n8n)

Endpoints para integración con n8n.

## Autenticación

Usar header X-N8N-API-Key con el API key configurado en N8N_API_KEY.

## Endpoints

### GET /api/v1/automation/today/

Eventos del día actual.

### GET /api/v1/automation/upcoming/

Próximos eventos.

### POST /api/v1/automation/events/

Crear propuesta de evento.

### POST /api/v1/automation/events/{uuid}/confirm/

Confirmar propuesta de evento.

### GET /api/v1/integrations/health/

Health check.

## Webhooks

Los webhooks se firman con HMAC-SHA256.

Headers:
- X-FamilyCalendar-Signature
- X-FamilyCalendar-Timestamp
- X-FamilyCalendar-Event
