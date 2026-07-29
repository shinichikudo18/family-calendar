from django.contrib import admin
from django.urls import path, include
from notifications import views as notification_views

urlpatterns = [
    path('', include('web.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/events/', include('events.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/automation/today/', notification_views.automation_today, name='automation-today'),
    path('api/v1/automation/upcoming/', notification_views.automation_upcoming, name='automation-upcoming'),
    path('api/v1/automation/events/', notification_views.automation_create_event, name='automation-create-event'),
    path('api/v1/automation/events/<uuid:uuid>/confirm/', notification_views.automation_confirm_event, name='automation-confirm-event'),
    path('api/v1/integrations/health/', notification_views.integration_health, name='integration-health'),
]
