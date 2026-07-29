# Despliegue

## Stack

- Django + Gunicorn en CT Debian (:8000 interno)
- Nginx como proxy reverso (externo)
- PostgreSQL + Redis en el mismo CT
- Celery workers para tareas async

## Servicios systemd

- family-calendar-gunicorn.service
- family-calendar-celery.service
- family-calendar-beat.service

## Firewall

Solo permitir acceso a puerto 8000 desde IP del Nginx.
