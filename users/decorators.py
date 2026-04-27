from __future__ import annotations

from functools import wraps
from typing import Callable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def user_in_group(user, group_name: str) -> bool:
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name=group_name).exists())


def admin_required(view_func: Callable) -> Callable:
    @wraps(view_func)
    @login_required
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if user_in_group(request.user, "admin"):
            return view_func(request, *args, **kwargs)
        messages.error(request, "No tienes permiso para realizar esta accion.")
        return redirect("dashboard")

    return _wrapped


def cashier_or_admin_required(view_func: Callable) -> Callable:
    @wraps(view_func)
    @login_required
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if user_in_group(request.user, "admin") or user_in_group(request.user, "cajero"):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Tu usuario no tiene un rol operativo asignado.")
        return redirect("dashboard")

    return _wrapped

