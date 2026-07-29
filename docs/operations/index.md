---
project: Family Calendar
status: draft
version: 0.2.0
tags:
  - operations
  - monitoring
---

# Operaciones

## Servicios systemd

- family-calendar-gunicorn.service (puerto 8000)
- family-calendar-celery.service (worker)
- family-calendar-beat.service (scheduler)

## Comandos utiles

- systemctl status family-calendar-gunicorn
- journalctl -u family-calendar-gunicorn -f
- systemctl restart family-calendar-gunicorn

## Firewall

nftables configurado para permitir:
- SSH (22) desde cualquier origen
- Gunicorn (8000) solo desde 192.168.22.254 (Nginx)
- ICMP (ping)

## Logs

/var/log/family-calendar/

## Backup

Base de datos:
pg_dump -U calendar_user family_calendar > backup.sql

## Health check

GET /api/v1/integrations/health/
Header: X-N8N-API-Key
