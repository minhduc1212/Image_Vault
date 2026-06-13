"""
Views for the Image Vault API.

Sections:
    Auth views    – register, login, me
    Vault views   – CRUD + join / leave / add_member
    Photo views   – list / create per vault, delete
    Comment views – create per photo, delete
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import User, Vault, Photo, Comment
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    VaultSerializer,
    VaultCreateSerializer,
    JoinVaultSerializer,
    AddMemberSerializer,
    PhotoSerializer,
    PhotoCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    AdminUserSerializer,
    AdminVaultSerializer,
    AdminPhotoSerializer,
    AdminCommentSerializer,
)


# =============================================================================
# Auth
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """POST /api/auth/register/ — create account, return token + user."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """POST /api/auth/login/ — authenticate, return token + user."""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """GET /api/auth/me/ — return current user info."""
    return Response(
        UserSerializer(request.user, context={'request': request}).data,
        status=status.HTTP_200_OK,
    )


# =============================================================================
# Vaults
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vault_list_create(request):
    """
    GET  /api/vaults/ — list all vaults the current user is a member of.
    POST /api/vaults/ — create a new vault (owner auto-added as member).
    """
    if request.method == 'GET':
        vaults = Vault.objects.filter(members=request.user).prefetch_related('members', 'photos')
        return Response(VaultSerializer(vaults, many=True).data)

    # POST — create vault
    serializer = VaultCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    vault = serializer.save(owner=request.user)
    vault.members.add(request.user)           # owner is automatically a member
    return Response(
        VaultSerializer(vault).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vault_join(request):
    """POST /api/vaults/join/ — join a vault via invite_code."""
    serializer = JoinVaultSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    vault = serializer.context['vault']

    if vault.members.filter(pk=request.user.pk).exists():
        return Response(
            {'detail': 'You are already a member of this vault.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    vault.members.add(request.user)
    return Response(VaultSerializer(vault).data, status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def vault_detail_delete(request, vault_id):
    """
    GET    /api/vaults/{id}/ — vault detail (must be member).
    DELETE /api/vaults/{id}/ — delete vault (owner only).
    """
    vault = get_object_or_404(Vault, pk=vault_id)

    # Only members can see or delete this vault
    if not vault.members.filter(pk=request.user.pk).exists():
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(VaultSerializer(vault).data)

    # DELETE — owner only
    if vault.owner != request.user:
        return Response(
            {'detail': 'Only the vault owner can delete it.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    vault.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vault_leave(request, vault_id):
    """POST /api/vaults/{id}/leave/ — leave a vault (owner cannot leave)."""
    vault = get_object_or_404(Vault, pk=vault_id)

    if not vault.members.filter(pk=request.user.pk).exists():
        return Response({'detail': 'You are not a member of this vault.'}, status=status.HTTP_400_BAD_REQUEST)

    if vault.owner == request.user:
        return Response(
            {'detail': 'The vault owner cannot leave. Transfer ownership or delete the vault.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    vault.members.remove(request.user)
    return Response({'detail': 'You have left the vault.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vault_add_member(request, vault_id):
    """POST /api/vaults/{id}/add_member/ — add user by email (owner only)."""
    vault = get_object_or_404(Vault, pk=vault_id)

    if vault.owner != request.user:
        return Response(
            {'detail': 'Only the vault owner can add members.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AddMemberSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    new_member = serializer.context['new_member']

    if vault.members.filter(pk=new_member.pk).exists():
        return Response(
            {'detail': 'This user is already a member of the vault.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    vault.members.add(new_member)
    return Response(VaultSerializer(vault).data, status=status.HTTP_200_OK)


# =============================================================================
# Photos
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def photo_list_create(request, vault_id):
    """
    GET  /api/vaults/{id}/photos/ — list photos in vault (members only).
    POST /api/vaults/{id}/photos/ — post a photo to the vault.
    """
    vault = get_object_or_404(Vault, pk=vault_id)

    if not vault.members.filter(pk=request.user.pk).exists():
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        photos = vault.photos.select_related('uploader').prefetch_related('comments__author')
        return Response(PhotoSerializer(photos, many=True).data)

    # POST — add photo
    serializer = PhotoCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    photo = serializer.save(vault=vault, uploader=request.user)
    return Response(
        PhotoSerializer(photo).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def photo_delete(request, photo_id):
    """DELETE /api/photos/{id}/ — delete photo (uploader only)."""
    photo = get_object_or_404(Photo, pk=photo_id)

    # Must be a member of the vault to even know the photo exists
    if not photo.vault.members.filter(pk=request.user.pk).exists():
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if photo.uploader != request.user:
        return Response(
            {'detail': 'Only the uploader can delete this photo.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    photo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Comments
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, photo_id):
    """POST /api/photos/{id}/comments/ — add a comment (vault members only)."""
    photo = get_object_or_404(Photo, pk=photo_id)

    if not photo.vault.members.filter(pk=request.user.pk).exists():
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CommentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    comment = serializer.save(photo=photo, author=request.user)
    return Response(
        CommentSerializer(comment).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_id):
    """DELETE /api/comments/{id}/ — delete comment (author only)."""
    comment = get_object_or_404(Comment, pk=comment_id)

    # Must be a member of the vault
    if not comment.photo.vault.members.filter(pk=request.user.pk).exists():
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if comment.author != request.user:
        return Response(
            {'detail': 'Only the comment author can delete this comment.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Admin Panel Views
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_stats(request):
    """GET /api/admin/stats/ - Get database overview stats."""
    total_users = User.objects.count()
    total_vaults = Vault.objects.count()
    total_photos = Photo.objects.count()
    total_comments = Comment.objects.count()

    recent_users = User.objects.order_by('-created_at')[:5]
    recent_photos = Photo.objects.order_by('-posted_at')[:5]

    return Response({
        'stats': {
            'users': total_users,
            'vaults': total_vaults,
            'photos': total_photos,
            'comments': total_comments,
        },
        'recent_users': UserSerializer(recent_users, many=True, context={'request': request}).data,
        'recent_photos': PhotoSerializer(recent_photos, many=True, context={'request': request}).data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_users_list(request):
    """GET /api/admin/users/ - List all users."""
    users = User.objects.order_by('-created_at')
    serializer = AdminUserSerializer(users, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_user_detail(request, user_id):
    """
    PATCH  /api/admin/users/{id}/ - Edit is_staff / is_active / name / email.
    DELETE /api/admin/users/{id}/ - Delete user.
    """
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'PATCH':
        serializer = AdminUserSerializer(user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        if request.user == user:
            return Response({'detail': 'You cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_vaults_list(request):
    """GET /api/admin/vaults/ - List all vaults."""
    vaults = Vault.objects.order_by('-created_at')
    serializer = AdminVaultSerializer(vaults, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_vault_detail(request, vault_id):
    """
    PATCH  /api/admin/vaults/{id}/ - Update vault name/description/emoji/owner.
    DELETE /api/admin/vaults/{id}/ - Delete vault.
    """
    vault = get_object_or_404(Vault, pk=vault_id)

    if request.method == 'PATCH':
        serializer = AdminVaultSerializer(vault, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        vault.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_photos_list(request):
    """GET /api/admin/photos/ - List all photos."""
    photos = Photo.objects.order_by('-posted_at')
    serializer = AdminPhotoSerializer(photos, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_photo_detail(request, photo_id):
    """DELETE /api/admin/photos/{id}/ - Delete photo."""
    photo = get_object_or_404(Photo, pk=photo_id)
    photo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_comments_list(request):
    """GET /api/admin/comments/ - List all comments."""
    comments = Comment.objects.order_by('-posted_at')
    serializer = AdminCommentSerializer(comments, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_comment_detail(request, comment_id):
    """DELETE /api/admin/comments/{id}/ - Delete comment."""
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
