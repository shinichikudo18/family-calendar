import logging
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import NotificationChannel, NotificationRule, WebhookEndpoint, WebhookDelivery
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


def _get_user_family_ids(user):
    from accounts.models import FamilyMember
    return FamilyMember.objects.filter(
        user=user, is_active=True
    ).values_list('family_id', flat=True)


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


def _get_user_from_request(request):
    n8n_user = request.headers.get('X-N8N-User')
    if n8n_user:
        from django.contrib.auth.models import User
        try:
            return User.objects.get(username=n8n_user)
        except User.DoesNotExist:
            pass
    if request.user.is_authenticated:
        return request.user
    return None


@api_view(['GET'])
@permission_classes([AllowAny])
def automation_today(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    from events.models import Event, Calendar
    from events.serializers import EventSerializer
    today = timezone.localdate()
    start = timezone.make_aware(timezone.datetime(today.year, today.month, today.day))
    end = start + timezone.timedelta(days=1)
    events = Event.objects.filter(
        start_time__lt=end, end_time__gte=start,
        is_cancelled=False, is_proposal=False
    )[:50]
    return Response({
        'date': today.isoformat(),
        'events': EventSerializer(events, many=True).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def automation_upcoming(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    from events.models import Event, Calendar
    from events.serializers import EventSerializer
    now = timezone.now()
    events = Event.objects.filter(
        start_time__gte=now, is_cancelled=False, is_proposal=False
    ).order_by('start_time')[:10]
    return Response({'events': EventSerializer(events, many=True).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def automation_create_event(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    from events.models import Calendar, EventProposal
    serializer = AutomationEventSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    calendar_id = data.get('calendar_id')
    if not calendar_id:
        families = _get_user_family_ids(request.user) if request.user.is_authenticated else []
        cal = Calendar.objects.filter(family_id__in=families, is_active=True).first()
        if cal:
            calendar_id = cal.id
    proposal = EventProposal.objects.create(
        calendar_id=calendar_id,
        title=data['title'],
        description=data.get('description', ''),
        start_time=data['start_time'],
        end_time=data['end_time'],
        all_day=data.get('all_day', False),
    )
    return Response({
        'status': 'proposal',
        'proposal_id': str(proposal.id),
        'message': 'Event proposal created. Waiting for confirmation.',
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def automation_confirm_event(request, uuid):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    from events.models import EventProposal, Event, Calendar
    try:
        proposal = EventProposal.objects.get(id=uuid, status='pending')
    except EventProposal.DoesNotExist:
        return Response({'error': 'Proposal not found or already processed'}, status=status.HTTP_404_NOT_FOUND)
    event = Event.objects.create(
        calendar=proposal.calendar,
        title=proposal.title,
        description=proposal.description,
        start_time=proposal.start_time,
        end_time=proposal.end_time,
        all_day=proposal.all_day,
    )
    proposal.status = 'confirmed'
    proposal.confirmed_event = event
    proposal.save()
    return Response({'status': 'confirmed', 'event_id': str(event.id)})


@api_view(['GET'])
@permission_classes([AllowAny])
def integration_health(request):
    if not _check_n8n_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '0.2.0',
    })
