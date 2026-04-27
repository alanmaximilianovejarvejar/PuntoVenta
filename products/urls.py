from django.urls import path

from products import views


urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("nuevo/", views.product_create, name="product_create"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("<int:pk>/editar/", views.product_update, name="product_update"),
    path("<int:pk>/desactivar/", views.product_deactivate, name="product_deactivate"),
    path("categorias/", views.category_list, name="category_list"),
    path("categorias/nueva/", views.category_create, name="category_create"),
]

