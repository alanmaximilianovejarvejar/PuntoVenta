from django.contrib.auth.models import User
from django.shortcuts import render

from users.decorators import admin_required


@admin_required
def user_list(request):
    users = User.objects.prefetch_related("groups").order_by("username")
    return render(request, "users/user_list.html", {"users": users})

