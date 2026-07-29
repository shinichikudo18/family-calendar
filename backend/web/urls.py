from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('calendario/', views.MonthCalendarView.as_view(), name='calendar_view'),
    path('eventos/nuevo/', views.EventCreateHtmxView.as_view(), name='event_create_htmx'),
]
