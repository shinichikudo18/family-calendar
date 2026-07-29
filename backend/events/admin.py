from django.contrib import admin
from .models import Calendar, Event, EventParticipant, EventCategory


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'family', 'color', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'calendar', 'start_time', 'end_time', 'all_day', 'is_cancelled']
    list_filter = ['all_day', 'is_cancelled', 'calendar']
    search_fields = ['title', 'description']


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'user', 'status']
    list_filter = ['status']


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'family', 'color']
