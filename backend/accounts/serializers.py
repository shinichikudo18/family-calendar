from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Family, FamilyMember


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    invite_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'invite_code']

    def create(self, validated_data):
        invite_code = validated_data.pop('invite_code', '')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if invite_code:
            try:
                family = Family.objects.get(invite_code=invite_code)
                FamilyMember.objects.create(
                    family=family, user=user, role='member'
                )
            except Family.DoesNotExist:
                pass
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class FamilySerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = ['id', 'name', 'slug', 'invite_code', 'member_count',
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'invite_code', 'created_by',
                            'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()


class FamilyMemberSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = FamilyMember
        fields = ['id', 'family', 'user', 'user_details', 'role',
                  'is_active', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class JoinFamilySerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=20)
