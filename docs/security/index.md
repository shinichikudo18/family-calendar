# Seguridad

## Políticas

- No almacenar secrets en el repositorio
- Webhooks firmados con HMAC-SHA256
- API keys rotables por servicio
- HTTPS obligatorio en producción
- Rate limiting en login y API
- Bloqueo de rutas internas (/admin/) desde WAN

## Variables de entorno

Todas las credenciales via .env. Ver .env.example.

## Headers de seguridad

- Strict-Transport-Security
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection
- Referrer-Policy
