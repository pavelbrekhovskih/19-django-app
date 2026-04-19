from random import random
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page

from .models import Profile


class HelloView(View):
    welcome_message = _("welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items
        )
        products_line = products_line.format(count=items)

        return HttpResponse(f"<h1>{self.welcome_message}</h1>"
                            f"<h2>{products_line}</h2>")


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    # Вызов этого метода пр-т тогда, когда форма была опубликована успешно
    def form_valid(self, form):
        response = super().form_valid(form)  # здесь поль-ль уже сохранён
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)

        return response


# Создаём отображение страницы входа и обработку входа
# + обр-ку сит-и, когда польз-ль поп-т на страницу входа с выполненным входом
# - тогда его надо перенаправить на осн-ю страницу
# (В Django в каждом объекте request содержится объект user)

# переписали с помощью view класса в urls.py
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")

        return render(request, "myauth/login.html")

    # Обраб-м сит-ю, когда поль-лб опубликовал форму
    username = request.POST["username"]
    password = request.POST["password"]

    # попытаемся аутентифицир-ть польз-ля
    # ф-я вернёт или польз-ля или None
    user = authenticate(request, username=username, password=password)

    if user:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", context={"error": "Invalid login credentials"})


# переписали с помощью view класса в urls.py
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)

    return redirect(reverse("myauth:login"))


class MyLogOutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


# @user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    response = HttpResponse("Cookie set")
    response.set_cookie("fize", "buzz", max_age=3600)

    return response

@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fize", "default_value")

    # после 1-го запроса рез-т будет браться из кеша
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth:view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"  # устан-м зн-е в словарь сессии
    # и Dj сохраняет эти данные и уст-т токен сессии в бр-ре польз-ля
    # явное сохранение / установку делать не нужно
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default_value")

    return HttpResponse(f"Session value: {value!r}")


class FoobarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
