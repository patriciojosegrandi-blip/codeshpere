```python
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Post, Profile


# ==========================================
# CONFIGURACIÓN
# ==========================================

def get_verified_users():
    """
    Lee los usuarios verificados desde verified.txt.
    Ignora líneas vacías y diferencias entre mayúsculas/minúsculas.
    """

    verified_file = Path(settings.BASE_DIR) / "verified.txt"

    if not verified_file.exists():
        return set()

    try:
        return {
            line.strip().casefold()
            for line in verified_file.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        }
    except OSError:
        return set()


# ==========================================
# HOME
# ==========================================

@login_required
def home(request):
    posts = Post.objects.select_related(
        "user"
    ).all().order_by("-created_at")

    return render(request, "home.html", {
        "posts": posts
    })


# ==========================================
# LOGIN
# ==========================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("/")

        return HttpResponse(
            "Usuario o contraseña incorrectos ❌",
            status=401
        )

    return render(request, "login.html")


# ==========================================
# LOGOUT
# ==========================================

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login/")


# ==========================================
# REGISTER
# ==========================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return HttpResponse(
                "Completá todos los campos ❌",
                status=400
            )

        if len(username) > 150:
            return HttpResponse(
                "El nombre de usuario es demasiado largo ❌",
                status=400
            )

        if User.objects.filter(username__iexact=username).exists():
            return HttpResponse(
                "Ese usuario ya existe ❌",
                status=409
            )

        if len(password) < 8:
            return HttpResponse(
                "La contraseña debe tener al menos 8 caracteres ❌",
                status=400
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Profile.objects.get_or_create(user=user)

        return redirect("/login/")

    return render(request, "register.html")


# ==========================================
# CREAR PUBLICACIÓN
# ==========================================

@login_required
def create_post(request):

    if request.method == "POST":

        content = request.POST.get("content", "").strip()

        if not content:
            return HttpResponse(
                "La publicación no puede estar vacía ❌",
                status=400
            )

        Post.objects.create(
            user=request.user,
            content=content
        )

        return redirect("/")

    return render(request, "create_post.html")


# ==========================================
# PERFIL PROPIO
# ==========================================

@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        profile.bio = request.POST.get("bio", "").strip()
        profile.save()

        return redirect("/profile/")

    return render(request, "profile.html", {
        "profile": profile
    })


# ==========================================
# PERFIL PÚBLICO DE OTRO USUARIO
# ==========================================

def user_profile(request, username):

    user_profile = get_object_or_404(
        User,
        username=username
    )

    profile, created = Profile.objects.get_or_create(
        user=user_profile
    )

    posts = Post.objects.filter(
        user=user_profile
    ).order_by("-created_at")

    verified_users = get_verified_users()

    is_verified = (
        user_profile.username.casefold() in verified_users
    )

    return render(request, "user_profile.html", {
        "profile": profile,
        "user_profile": user_profile,
        "posts": posts,
        "is_verified": is_verified
    })
```
