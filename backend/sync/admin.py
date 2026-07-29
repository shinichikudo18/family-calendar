from django.contrib import admin
from .models import SyncProvider, SyncLog


@admin.register(SyncProvider)
class SyncProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'family', 'provider_type', 'sync_mode', 'is_enabled', 'last_sync_at']
    list_filter = ['provider_type', 'sync_mode', 'is_enabled']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'status', 'events_imported', 'events_exported', 'started_at']
    list_filter = ['status']
