from rest_framework import permissions


class IsFamilyAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = obj.members.filter(
            user=request.user, role='admin', is_active=True
        ).first()
        return membership is not None


class IsFamilyMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.members.filter(
            user=request.user, is_active=True
        ).exists()


class CanManageFamily(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = obj.members.filter(
            user=request.user, is_active=True
        ).first()
        if not membership:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return membership.role == 'admin'
