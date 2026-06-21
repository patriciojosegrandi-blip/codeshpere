from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Post, Profile


# HOME
@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, "home.html", {"posts": posts})


# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return HttpResponse("Usuario o contraseña incorrectos ❌")

    return render(request, "login.html")


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("/login/")


# REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return HttpResponse("Ese usuario ya existe ❌")

        user = User.objects.create_user(username=username, password=password)

        # crear profile automáticamente
        Profile.objects.create(user=user)

        return redirect("/login/")

    return render(request, "register.html")


# CREAR POST
@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST["content"]

        image = request.FILES.get("image")

        Post.objects.create(
            user=request.user,
            content=content,
            image=image
        )

        return redirect("/")

    return render(request, "create_post.html")


# PERFIL DEL USUARIO LOGUEADO
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio", "")

        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]

        profile.save()

        return redirect("/profile/")

    return render(request, "profile.html", {"profile": profile})


# PERFIL DE OTRO USUARIO (🔥 ESTE ES EL ARREGLADO)
def user_profile(request, username):
    user = get_object_or_404(User, username=username)

    profile, created = Profile.objects.get_or_create(user=user)

    posts = Post.objects.filter(user=user).order_by('-created_at')

    return render(request, "user_profile.html", {
        "profile": profile,
        "user_profile": user,
        "posts": posts
    })