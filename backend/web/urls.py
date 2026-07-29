from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('calendario/', views.MonthCalendarView.as_view(), name='calendar_view'),
    path('familia/', views.FamilyListView.as_view(), name='family_members'),
    path('eventos/nuevo/', views.EventCreateHtmxView.as_view(), name='event_create_htmx'),
    path('configuracion/', views.SettingsView.as_view(), name='settings'),
    path('auth/google/', views.GoogleAuthStartView.as_view(), name='google_auth_start'),
    path('auth/google/callback/', views.GoogleAuthCallbackView.as_view(), name='google_auth_callback'),
    path('auth/google/disconnect/', views.GoogleDisconnectView.as_view(), name='google_disconnect'),
]
