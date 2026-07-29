# Changelog

Todas las changes notables de Family Calendar.

## [0.1.0] - 2026-07-29

### Added
- Estructura monorepo inicial
- Proyecto Django con PostgreSQL, Redis y Celery
- App notifications con modelos: NotificationChannel, NotificationRule, WebhookEndpoint, WebhookDelivery
- Webhooks firmados con HMAC-SHA256
- API REST para n8n: /api/v1/automation/, /api/v1/integrations/
- Configuración Gunicorn con systemd
- Ejemplo de virtual host Nginx con HTTPS, rate limiting y seguridad
- Pipeline CI/CD con GitHub Actions (lint, test, security)
- Documentación inicial compatible con Obsidian
- Issue templates y PR template
