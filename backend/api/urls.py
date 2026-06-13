"""
URL configuration for the Image Vault API.

All routes are under /api/ (configured in core/urls.py).
"""

from django.urls import path
from . import views

urlpatterns = [
    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    path('auth/register/', views.register,  name='auth-register'),
    path('auth/login/',    views.login,     name='auth-login'),
    path('auth/me/',       views.me,        name='auth-me'),

    # ------------------------------------------------------------------
    # Vaults
    # ------------------------------------------------------------------
    path('vaults/',                        views.vault_list_create,  name='vault-list-create'),
    path('vaults/join/',                   views.vault_join,         name='vault-join'),
    path('vaults/<uuid:vault_id>/',        views.vault_detail_delete,name='vault-detail-delete'),
    path('vaults/<uuid:vault_id>/leave/',  views.vault_leave,        name='vault-leave'),
    path('vaults/<uuid:vault_id>/add_member/', views.vault_add_member, name='vault-add-member'),

    # ------------------------------------------------------------------
    # Photos
    # ------------------------------------------------------------------
    path('vaults/<uuid:vault_id>/photos/', views.photo_list_create, name='photo-list-create'),
    path('photos/<uuid:photo_id>/',        views.photo_delete,      name='photo-delete'),

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------
    path('photos/<uuid:photo_id>/comments/', views.comment_create, name='comment-create'),
    path('comments/<uuid:comment_id>/',      views.comment_delete, name='comment-delete'),
]
