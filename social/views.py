from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Post, Profile, Like


# ==========================================
# CONFIGURACIÓN
# ==========================================

def get_verified_users():
    verified_file = Path(settings.BASE_DIR) / "verified.txt"

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


def get_safe_return_url(request):
    referer = request.META.get("HTTP_REFERER", "")

    if url_has_allowed_host_and_scheme(
        referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        return referer

    return "/"


# ==========================================
# HOME
# ==========================================

@login_required
def home(request):
    posts = Post.objects.select_related(
        "user"
    ).prefetch_related(
        "likes"
    ).all().order_by("-created_at")

    liked_post_ids = set(
        Like.objects.filter(
            user=request.user
        ).values_list("post_id", flat=True)
    )

    return render(request, "home.html", {
        "posts": posts,
        "liked_post_ids": liked_post_ids
    })


# ==========================================
# LIKES
# ==========================================

@login_required
def like_post(request, post_id):

    if request.method != "POST":
        return HttpResponse("Método no permitido", status=405)

    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        like.delete()

    return redirect(get_safe_return_url(request))


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

    verified_users = get_verified_users()

    is_verified = (
        request.user.username.casefold() in verified_users
    )

    return render(request, "profile.html", {
        "profile": profile,
        "is_verified": is_verified
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
    ).select_related(
        "user"
    ).prefetch_related(
        "likes"
    ).order_by("-created_at")

    verified_users = get_verified_users()

    is_verified = (
        user_profile.username.casefold() in verified_users
    )

    liked_post_ids = set()

    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(
                user=request.user
            ).values_list("post_id", flat=True)
        )

    return render(request, "user_profile.html", {
        "profile": profile,
        "user_profile": user_profile,
        "posts": posts,
        "is_verified": is_verified,
        "liked_post_ids": liked_post_ids
    })
