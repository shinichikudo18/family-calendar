---
project: Family Calendar
status: draft
version: 0.2.0
tags:
  - architecture
  - django
---

# Arquitectura

## Stack

- Backend: Django 5.1 + Django REST Framework
- Database: PostgreSQL 16
- Cache/Queue: Redis 7 + Celery
- Server: Gunicorn
- Proxy: Nginx (externo)
- Auth: JWT + LDAP
- Automation: n8n
- Notificaciones: Telegram/WhatsApp via n8n

## Componentes

Nginx (443) -> Gunicorn (8000) -> Django REST API
Django -> PostgreSQL, Redis
Celery Workers -> Redis
n8n -> Django API (automation)
Django -> n8n webhooks (notifications)
Android -> Django API
LDAP -> Django (auth)

## Flujo de datos

1. Cliente HTTPS -> Nginx -> Gunicorn -> Django
2. Django -> PostgreSQL (datos persistentes)
3. Django -> Redis (cache + task queue)
4. Celery -> Redis (task scheduling)
5. n8n -> Django API (automation)
6. Django -> n8n webhooks (notificaciones)
