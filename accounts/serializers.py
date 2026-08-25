from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from .models import UserRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source='is_admin_user', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'name', 'email', 'role', 'is_admin', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'is_admin')


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'name', 'phone')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=UserRole.USER,
            name=validated_data.get('name', validated_data['username'])
        )

        from library.models import Member
        Member.objects.create(
            user=user,
            name=user.name or user.username,
            email=user.email,
            phone=phone or "N/A",
            active_status=True
        )

        return user


# Backward compatibility alias
RegisterSerializer = UserSignupSerializer



class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    admin_secret_key = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'name', 'admin_secret_key')

    def validate_admin_secret_key(self, value):
        expected_secret = getattr(settings, 'ADMIN_SECRET_KEY', 'library-admin-secret-2026')
        if value != expected_secret:
            raise serializers.ValidationError("Invalid Admin Secret Key. Administrator account creation rejected.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('admin_secret_key')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=UserRole.ADMIN,
            is_staff=True,
            name=validated_data.get('name', validated_data['username'])
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = UserSerializer(self.user).data
        data['user'] = user_data
        return data
