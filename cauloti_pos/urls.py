import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core import views as core_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="users/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", core_views.dashboard, name="dashboard"),
    path("health/", core_views.health, name="health"),
    path("sync/", include("core.urls")),
    path("usuarios/", include("users.urls")),
    path("productos/", include("products.urls")),
    path("ventas/", include("sales.urls")),
    path("inventario/", include("inventory.urls")),
]

if settings.DEBUG or os.environ.get("CAULOTI_SERVE_MEDIA", "0") == "1":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
