---
project: Family Calendar
status: draft
version: 0.2.0
tags:
  - n8n
  - automation
---

# n8n Integration

## URL

https://brain.katherine.cl:88

## Endpoints disponibles

- GET /api/v1/automation/today/
- GET /api/v1/automation/upcoming/
- POST /api/v1/automation/events/
- POST /api/v1/automation/events/{uuid}/confirm/
- GET /api/v1/integrations/health/

## Webhooks entrantes (n8n -> Django)

n8n llama a la API de Django con header X-N8N-API-Key.

## Webhooks salientes (Django -> n8n)

Django envia notificaciones a n8n via:

POST https://brain.katherine.cl:88/webhook/family-calendar-notify

Payload: { to, provider, title, message, event_type, timestamp }

## Eventos

- event_reminder: Recordatorio de evento
- daily_summary: Resumen diario
- weekly_summary: Resumen semanal
- sync_error: Error de sincronizacion
- calendar_conflict: Conflicto de calendario
