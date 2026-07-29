# LDAP Integration

## Configuracion

Servidor OpenLDAP en 192.168.22.224:3890.

## Estructura

- Base DN: ou=people,dc=katherine,dc=cl
- Identificador de usuario: uid
- Atributos: cn (nombre completo), mail, uid

## Autenticacion

Django usa django-auth-ldap con dos backends:
1. LDAPBackend (prioridad)
2. ModelBackend (fallback local)

Los usuarios LDAP se crean automaticamente en Django al primer login.
