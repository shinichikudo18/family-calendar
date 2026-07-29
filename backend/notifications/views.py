import logging
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    NotificationChannel, NotificationRule,
    WebhookEndpoint, WebhookDelivery,
)
from .serializers import (
    NotificationChannelSerializer, NotificationRuleSerializer,
    WebhookEndpointSerializer, WebhookDeliverySerializer,
    AutomationEventSerializer,
)

logger = logging.getLogger(__name__)


def _check_n8n_key(request):
    n8n_key = request.headers.get('X-N8N-API-Key', '')
    expected = getattr(settings, 'N8N_API_KEY', '')
    if not expected or n8n_key != expected:
        return False
    return True


class NotificationChannelViewSet(viewsets.ModelViewSet):
    queryset = NotificationChannel.objects.all()
    serializer_class = NotificationChannelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class NotificationRuleViewSet(viewsets.ModelViewSet):
    queryset = NotificationRule.objects.all()
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebhookDelivery.objects.all()
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']


@api_view(['GET'])
@permission_classes([AllowAny])
def automation_today(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    today = timezone.localdate()
    return Response({'date': today.isoformat(), 'events': [], 'user': None})


@api_view(['GET'])
@permission_classes([AllowAny])
def automation_upcoming(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'events': []})


@api_view(['POST'])
@permission_classes([AllowAny])
def automation_create_event(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = AutomationEventSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'status': 'proposal',
        'message': 'Event proposal created. Waiting for confirmation.',
        'data': serializer.validated_data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def automation_confirm_event(request, uuid):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'status': 'confirmed', 'event_id': str(uuid)})


@api_view(['GET'])
@permission_classes([AllowAny])
def integration_health(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '0.1.0',
    })
