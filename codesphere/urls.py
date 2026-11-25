"""
Rutas principales de CodeSphere.
Incluye autenticación local y autenticación con Google.
"""

from django.contrib import admin
from django.urls import path, include

from social import views


urlpatterns = [
    # Administración
    path("admin/", admin.site.urls),

    # Páginas principales
    path("", views.home, name="home"),

    # Autenticación tradicional
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    # Autenticación externa (Google)
    path("accounts/", include("allauth.urls")),

    # Publicaciones
    path("create/", views.create_post, name="create_post"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),

    # Perfiles
    path("profile/", views.profile_view, name="profile"),
    path("user/<str:username>/", views.user_profile, name="user_profile"),
]
