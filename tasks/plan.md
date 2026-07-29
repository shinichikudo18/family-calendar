# Implementation Plan: Family Calendar

## Overview
Calendario familiar con Django REST API, sincronizacion multi-calendario,
notificaciones via Telegram/WhatsApp con n8n, y app Android.

## Fases

### Fase 1: Fundacion (COMPLETADA)
- Crear repositorio y estructura monorepo
- Configurar Git y GitHub Actions
- Crear documentacion inicial
- Preparar CT Debian con PostgreSQL, Redis, Python
- Crear servicios systemd
- Crear app notifications con modelos y webhooks
- Configurar API endpoints para n8n

### Fase 2: Configurar reverse proxy Nginx

### Fase 3: Autenticacion local, familia, miembros y roles

### Fase 4: Calendario local

### Fase 5: API REST para APK y n8n

### Fase 6: Integracion LDAP

### Fase 7: Motor de sincronizacion

### Fase 8: Microsoft Calendar (IMPORT_ONLY)

### Fase 9: Google Calendar (IMPORT_ONLY)

### Fase 10: Integracion n8n, Telegram y WhatsApp

### Fase 11: Documentacion Obsidian completa

### Fase 12: Sincronizacion bidireccional

### Fase 13: APK Android

## Decisiones de Arquitectura

1. Monorepo con backend, android, infraestructura y docs
2. Webhooks firmados con HMAC-SHA256 + timestamps
3. Nginx externo como unico punto de entrada HTTPS
4. Gunicorn escuchando solo en puerto interno (:8000)
5. n8n como capa de automatizacion, no base de datos
6. API key de servicio para n8n (no OAuth de usuario)
7. Creacion de eventos via bots con flujo de confirmacion
