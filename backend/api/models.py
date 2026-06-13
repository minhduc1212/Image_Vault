"""
Models for the Image Vault API.

Models:
    User    – custom user model (email-based auth, auto initials)
    Vault   – photo vault with invite code and member management
    Photo   – photo entry inside a vault
    Comment – comment on a photo
"""

import uuid
import random
import string

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_initials(name: str) -> str:
    """Return up to 2 uppercase initials derived from *name*."""
    words = name.strip().split()
    initials = ''.join(w[0].upper() for w in words if w)
    return initials[:2]


def _generate_invite_code() -> str:
    """Return a 6-character uppercase alphanumeric string."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=6))


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserManager(BaseUserManager):
    """Custom manager that uses email instead of username."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model.

    - email is the unique identifier (USERNAME_FIELD).
    - name replaces first_name / last_name.
    - initials are auto-computed and stored for quick access.
    - avatar is an optional image upload.
    """

    # Remove the default username field
    username = None

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    initials = models.CharField(max_length=2, editable=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        self.initials = _compute_initials(self.name) if self.name else ''
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} <{self.email}>'


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

class Vault(models.Model):
    """
    A named collection of photos shared between members.

    - invite_code is auto-generated (6 uppercase alphanumeric chars).
    - owner is automatically added to members on creation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    emoji = models.CharField(max_length=10, blank=True, default='🖼️')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_vaults',
    )
    members = models.ManyToManyField(
        User,
        related_name='member_vaults',
        blank=True,
    )
    invite_code = models.CharField(max_length=6, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vault'
        verbose_name_plural = 'Vaults'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate a unique invite code before first save
        if not self.invite_code:
            code = _generate_invite_code()
            # Ensure uniqueness (collision extremely unlikely but guard anyway)
            while Vault.objects.filter(invite_code=code).exists():
                code = _generate_invite_code()
            self.invite_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.emoji} {self.name}'


# ---------------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------------

class Photo(models.Model):
    """A photo posted inside a vault."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vault = models.ForeignKey(
        Vault,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_photos',
    )
    url = models.URLField(max_length=2048)
    caption = models.TextField(blank=True, default='')
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['-posted_at']

    def __str__(self):
        return f'Photo {self.id} in {self.vault.name}'


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class Comment(models.Model):
    """A comment left on a photo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['posted_at']

    def __str__(self):
        return f'Comment by {self.author.name} on photo {self.photo_id}'
