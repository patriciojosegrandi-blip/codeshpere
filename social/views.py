
from pathlib import Path
import random

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone

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
# ALGORITMO DEL FEED
# ==========================================

def generate_personalized_feed(user):
    # Obtener exclusivamente los likes del usuario actual.
    my_likes = Like.objects.filter(
        user=user
    ).select_related(
        "post",
        "post__user"
    )

    # Calcular interés por autor.
    author_scores = {}

    for like in my_likes:
        author_id = like.post.user_id

        # No utilizar likes propios para recomendarse a sí mismo.
        if author_id == user.id:
            continue

        author_scores[author_id] = (
            author_scores.get(author_id, 0) + 1
        )

    # Obtener publicaciones.
    all_posts = list(
        Post.objects.select_related(
            "user"
        ).prefetch_related(
            "likes"
        ).all()
    )

    personalized = []
    discovery = []
    own_posts = []

    now = timezone.now()

    for post in all_posts:

        if post.user_id == user.id:
            own_posts.append(post)
            continue

        score = author_scores.get(post.user_id, 0)

        # Impulso por antigüedad.
        age_hours = max(
            0,
            (now - post.created_at).total_seconds() / 3600
        )

        recency_bonus = max(
            0,
            2 - (age_hours / 72)
        )

        if score > 0:
            final_score = score * 3 + recency_bonus

            personalized.append(
                (post, final_score)
            )
        else:
            discovery.append(post)

    # Ordenar publicaciones personalizadas.
    personalized.sort(
        key=lambda item: (
            item[1],
            item[0].created_at
        ),
        reverse=True
    )

    # Aleatorizar descubrimientos.
    random.shuffle(discovery)

    # Construir feed.
    feed = []

    # Intercalar publicaciones para descubrir usuarios.
    discovery_index = 0

    for index, (post, score) in enumerate(personalized):

        feed.append(post)

        # Insertar descubrimientos periódicamente.
        if (
            (index + 1) % 4 == 0
            and discovery_index < len(discovery)
        ):
            feed.append(discovery[discovery_index])
            discovery_index += 1

    # Si hay pocos posts personalizados, igualmente
    # mostrar algunas recomendaciones aleatorias.
    if not personalized and discovery:
        feed.extend(discovery[:5])

    # Agregar publicaciones aleatorias restantes
    # para que el usuario pueda descubrir más personas.
    remaining_discovery = discovery[discovery_index:]

    if remaining_discovery:
        feed.extend(remaining_discovery[:3])

    # Intercalar algunas publicaciones propias.
    random.shuffle(own_posts)

    for own_post in own_posts:
        insert_at = random.randint(
            0,
            len(feed)
        ) if feed else 0

        feed.insert(insert_at, own_post)

    # Evitar duplicados.
    unique_feed = []
    seen_ids = set()

    for post in feed:
        if post.id not in seen_ids:
            unique_feed.append(post)
            seen_ids.add(post.id)

    return unique_feed


# ==========================================
# HOME
# ==========================================

@login_required
def home(request):

    posts = generate_personalized_feed(
        request.user
    )

    liked_post_ids = set(
        Like.objects.filter(
            user=request.user
        ).values_list(
            "post_id",
            flat=True
        )
    )

    verified_users = get_verified_users()

    verified_post_ids = {
        post.id
        for post in posts
        if post.user.username.casefold() in verified_users
    }

    return render(request, "home.html", {
        "posts": posts,
        "liked_post_ids": liked_post_ids,
        "verified_post_ids": verified_post_ids
    })


# ==========================================
# LIKES
# ==========================================

@login_required
def like_post(request, post_id):

    if request.method != "POST":
        return HttpResponse(
            "Método no permitido",
            status=405
        )

    post = get_object_or_404(
        Post,
        id=post_id
    )

    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        like.delete()

    return redirect(
        get_safe_return_url(request)
    )


# ==========================================
# LOGIN
# ==========================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

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

    return render(
        request,
        "login.html"
    )


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

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

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

        if User.objects.filter(
            username__iexact=username
        ).exists():
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

        Profile.objects.get_or_create(
            user=user
        )

        return redirect("/login/")

    return render(
        request,
        "register.html"
    )


# ==========================================
# CREAR PUBLICACIÓN
# ==========================================

@login_required
def create_post(request):

    if request.method == "POST":

        content = request.POST.get(
            "content",
            ""
        ).strip()

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

    return render(
        request,
        "create_post.html"
    )


# ==========================================
# PERFIL PROPIO
# ==========================================

@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        profile.bio = request.POST.get(
            "bio",
            ""
        ).strip()

        profile.save()

        return redirect("/profile/")

    verified_users = get_verified_users()

    is_verified = (
        request.user.username.casefold()
        in verified_users
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
    ).order_by(
        "-created_at"
    )

    verified_users = get_verified_users()

    is_verified = (
        user_profile.username.casefold()
        in verified_users
    )

    liked_post_ids = set()

    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(
                user=request.user
            ).values_list(
                "post_id",
                flat=True
            )
        )

    return render(request, "user_profile.html", {
        "profile": profile,
        "user_profile": user_profile,
        "posts": posts,
        "is_verified": is_verified,
        "liked_post_ids": liked_post_ids
    })
