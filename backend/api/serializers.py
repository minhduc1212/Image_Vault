"""
Serializers for the Image Vault API.

Hierarchy:
    UserMiniSerializer          – compact {id, name, initials} used inside nested objects
    UserSerializer              – full user response shape
    RegisterSerializer          – write-only input for registration
    CommentSerializer           – comment read + write
    PhotoSerializer             – photo read + write (nested comments + uploader)
    VaultSerializer             – vault read + write (nested members + photo_count)
    JoinVaultSerializer         – input for joining a vault via invite code
    AddMemberSerializer         – input for adding a member by email
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User, Vault, Photo, Comment


# ---------------------------------------------------------------------------
# Compact user representation used inside nested objects
# ---------------------------------------------------------------------------

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'initials']


# ---------------------------------------------------------------------------
# Full user response
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'initials', 'avatar', 'joined_at']
        read_only_fields = ['id', 'initials', 'joined_at']


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
        )
        return user


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            request=self.context.get('request'),
            username=data['email'].lower(),
            password=data['password'],
        )
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been disabled.')
        data['user'] = user
        return data


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class CommentSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(read_only=True)
    photo_id = serializers.UUIDField(source='photo.id', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'photo_id', 'author', 'text', 'posted_at']
        read_only_fields = ['id', 'photo_id', 'author', 'posted_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']


# ---------------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------------

class PhotoSerializer(serializers.ModelSerializer):
    uploader = UserMiniSerializer(read_only=True)
    vault_id = serializers.UUIDField(source='vault.id', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        fields = ['id', 'vault_id', 'uploader', 'url', 'caption', 'posted_at', 'comments']
        read_only_fields = ['id', 'vault_id', 'uploader', 'posted_at', 'comments']


class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['url', 'caption']


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

class VaultSerializer(serializers.ModelSerializer):
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)
    members = UserMiniSerializer(many=True, read_only=True)
    photo_count = serializers.SerializerMethodField()

    class Meta:
        model = Vault
        fields = [
            'id', 'name', 'description', 'emoji',
            'owner_id', 'members', 'invite_code',
            'created_at', 'photo_count',
        ]
        read_only_fields = ['id', 'owner_id', 'members', 'invite_code', 'created_at', 'photo_count']

    def get_photo_count(self, obj):
        return obj.photos.count()


class VaultCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vault
        fields = ['name', 'description', 'emoji']


# ---------------------------------------------------------------------------
# Join vault by invite code
# ---------------------------------------------------------------------------

class JoinVaultSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6, min_length=6)

    def validate_invite_code(self, value):
        try:
            vault = Vault.objects.get(invite_code=value.upper())
        except Vault.DoesNotExist:
            raise serializers.ValidationError('No vault found with this invite code.')
        self.context['vault'] = vault
        return value.upper()


# ---------------------------------------------------------------------------
# Add member by email (owner only)
# ---------------------------------------------------------------------------

class AddMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user found with this email.')
        self.context['new_member'] = user
        return value.lower()
