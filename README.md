# Family Calendar

Sistema de calendario familiar con sincronización multi-calendario (Google, Microsoft), bots de Telegram/WhatsApp, y app Android.

## Estructura del proyecto

family-calendar/
├── backend/          # Django REST API
├── android/          # App Android (futuro)
├── infrastructure/   # Nginx, systemd, scripts
├── n8n/              # Workflows n8n exportados
├── docs/             # Documentación (Markdown + Obsidian)
├── .github/          # GitHub Actions + templates
└── tasks/            # Plan de implementación

## Stack

- Backend: Django 5.x + Django REST Framework
- Base de datos: PostgreSQL 16
- Cache/Queue: Redis + Celery
- Servidor: Gunicorn
- Proxy: Nginx (externo)
- Automatización: n8n
- Notificaciones: Telegram + WhatsApp via n8n
- App móvil: Android (Kotlin, futuro)

## Fases de implementación

Ver [docs/installation/](docs/installation/) y [tasks/](tasks/) para el plan detallado.

## Seguridad

- No committear secrets, tokens ni contraseñas
- Usar .env.example como template
- Webhooks firmados con HMAC
- API keys rotables por servicio
