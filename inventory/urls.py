from django.urls import path

from inventory import views


urlpatterns = [
    path("", views.inventory_overview, name="inventory_overview"),
    path("ajuste/", views.inventory_adjustment, name="inventory_adjustment"),
]

