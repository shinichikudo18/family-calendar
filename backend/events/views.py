from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Calendar, Event, EventParticipant, EventCategory
from .serializers import (
    CalendarSerializer, EventSerializer, EventCreateSerializer,
    EventParticipantSerializer, EventCategorySerializer,
)
from accounts.permissions import IsFamilyMember


class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.filter(is_active=True)
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated, IsFamilyMember]

    def get_queryset(self):
        user_family_ids = self.request.user.family_memberships.filter(
            is_active=True
        ).values_list('family_id', flat=True)
        return Calendar.objects.filter(family_id__in=user_family_ids, is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_cancelled=False)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateSerializer
        return EventSerializer

    def get_queryset(self):
        user_family_ids = self.request.user.family_memberships.filter(
            is_active=True
        ).values_list('family_id', flat=True)
        calendars = Calendar.objects.filter(
            family_id__in=user_family_ids, is_active=True
        ).values_list('id', flat=True)

        qs = Event.objects.filter(calendar_id__in=calendars, is_cancelled=False)

        date_from = self.request.query_params.get('from')
        date_to = self.request.query_params.get('to')
        if date_from:
            qs = qs.filter(end_time__gte=date_from)
        if date_to:
            qs = qs.filter(start_time__lte=date_to)

        calendar_id = self.request.query_params.get('calendar')
        if calendar_id:
            qs = qs.filter(calendar_id=calendar_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        event = self.get_object()
        event.is_cancelled = True
        event.save()
        return Response({'status': 'cancelled'})

    @action(detail=False, methods=['get'])
    def today(self, request):
        now = timezone.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timezone.timedelta(days=1)
        qs = self.get_queryset().filter(
            start_time__lt=end, end_time__gte=start
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        now = timezone.now()
        qs = self.get_queryset().filter(start_time__gte=now)[:20]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class EventParticipantViewSet(viewsets.ModelViewSet):
    queryset = EventParticipant.objects.all()
    serializer_class = EventParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventParticipant.objects.filter(user=self.request.user)


class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [IsAuthenticated, IsFamilyMember]

    def get_queryset(self):
        user_family_ids = self.request.user.family_memberships.filter(
            is_active=True
        ).values_list('family_id', flat=True)
        return EventCategory.objects.filter(family_id__in=user_family_ids)
