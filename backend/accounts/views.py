from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Family, FamilyMember
from .serializers import (
    RegisterSerializer, UserSerializer,
    FamilySerializer, FamilyMemberSerializer,
    JoinFamilySerializer,
)
from .permissions import IsFamilyAdmin, IsFamilyMember, CanManageFamily


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)


class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer
    permission_classes = [IsAuthenticated, CanManageFamily]

    def get_queryset(self):
        user_family_ids = FamilyMember.objects.filter(
            user=self.request.user, is_active=True
        ).values_list('family_id', flat=True)
        return Family.objects.filter(id__in=user_family_ids)

    def perform_create(self, serializer):
        family = serializer.save(created_by=self.request.user)
        FamilyMember.objects.create(
            family=family, user=self.request.user, role='admin'
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request):
        serializer = JoinFamilySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            family = Family.objects.get(invite_code=serializer.validated_data['invite_code'])
        except Family.DoesNotExist:
            return Response(
                {'error': 'Invalid invite code'},
                status=status.HTTP_404_NOT_FOUND
            )

        if FamilyMember.objects.filter(
            family=family, user=request.user
        ).exists():
            return Response(
                {'error': 'Already a member'},
                status=status.HTTP_409_CONFLICT
            )

        FamilyMember.objects.create(
            family=family, user=request.user, role='member'
        )
        return Response({'status': 'joined'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsFamilyMember])
    def leave(self, request, pk=None):
        family = self.get_object()
        membership = FamilyMember.objects.filter(
            family=family, user=request.user, is_active=True
        ).first()
        if not membership:
            return Response(
                {'error': 'Not a member'},
                status=status.HTTP_404_NOT_FOUND
            )
        if membership.role == 'admin':
            admin_count = FamilyMember.objects.filter(
                family=family, role='admin', is_active=True
            ).count()
            if admin_count <= 1:
                return Response(
                    {'error': 'Last admin cannot leave. Transfer admin first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        membership.is_active = False
        membership.save()
        return Response({'status': 'left'})


class FamilyMemberViewSet(viewsets.ModelViewSet):
    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FamilyMember.objects.filter(
            user=self.request.user, is_active=True
        )
