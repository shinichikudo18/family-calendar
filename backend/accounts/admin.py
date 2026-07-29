from django.contrib import admin
from .models import Family, FamilyMember


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'invite_code', 'created_by', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['invite_code', 'slug']


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'family', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active']
