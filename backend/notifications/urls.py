from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'channels', views.NotificationChannelViewSet)
router.register(r'rules', views.NotificationRuleViewSet)
router.register(r'webhook-endpoints', views.WebhookEndpointViewSet)
router.register(r'webhook-deliveries', views.WebhookDeliveryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
