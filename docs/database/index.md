---
project: Family Calendar
status: draft
version: 0.2.0
tags:
  - database
  - postgresql
---

# Base de Datos

## Esquema

### accounts

- **Family**: id, name, slug, invite_code, created_by, created_at, updated_at
- **FamilyMember**: id, family, user, role (admin/member/viewer), is_active, joined_at

### events

- **Calendar**: id, family, name, color, description, created_by, is_active
- **Event**: id, calendar, title, description, start_time, end_time, all_day, location, is_recurring, recurrence_rule, is_cancelled, is_proposal, external_id, external_provider
- **EventParticipant**: id, event, user, status (pending/accepted/maybe/declined)
- **EventCategory**: id, family, name, color
- **EventProposal**: id, calendar, title, description, start_time, end_time, all_day, status, source_provider, confirmed_event

### notifications

- **NotificationChannel**: id, user, provider, external_recipient_id, is_enabled, verified_at
- **NotificationRule**: id, user, event_type, minutes_before, channel, is_enabled
- **WebhookEndpoint**: id, name, target_url, encrypted_signing_secret, allowed_event_types, is_enabled
- **WebhookDelivery**: id, endpoint, event_type, payload_hash, status, attempts, response_status

### sync

- **SyncProvider**: id, family, provider_type, sync_mode, credentials, is_enabled, last_sync_at
- **SyncLog**: id, provider, status, events_imported, events_exported, error_message

## Indices

- Event: (start_time, end_time), (calendar, start_time), (external_id, external_provider)
- WebhookDelivery: (status, created_at)
