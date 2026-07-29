# API REST

## Autenticacion

### POST /api/v1/auth/login/
Login con username y password. Retorna JWT access y refresh.

### POST /api/v1/auth/register/
Registro de nuevo usuario.

### GET /api/v1/auth/profile/
Perfil del usuario autenticado.

## Familias

### GET/POST /api/v1/auth/families/
Listar/Crear familias.

### POST /api/v1/auth/families/join/
Unirse a familia mediante invite_code.

## Eventos

### GET/POST /api/v1/events/calendars/
CRUD de calendarios.

### GET/POST /api/v1/events/events/
CRUD de eventos. Filtros: ?from=, ?to=, ?calendar=

### GET /api/v1/events/events/today/
Eventos del dia.

### GET /api/v1/events/events/upcoming/
Proximos 20 eventos.

### POST /api/v1/events/events/{id}/cancel/
Cancelar evento.

## n8n Automation

Endpoints para n8n. Autenticar con header X-N8N-API-Key.

### GET /api/v1/automation/today/
### GET /api/v1/automation/upcoming/
### POST /api/v1/automation/events/
### POST /api/v1/automation/events/{uuid}/confirm/
### GET /api/v1/integrations/health/

## Notificaciones

### CRUD /api/v1/notifications/channels/
### CRUD /api/v1/notifications/rules/
### CRUD /api/v1/notifications/webhook-endpoints/
### Read /api/v1/notifications/webhook-deliveries/
