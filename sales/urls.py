from django.urls import path

from sales import views


urlpatterns = [
    path("pos/", views.pos, name="pos"),
    path("buscar-productos/", views.search_products, name="search_products"),
    path("checkout/", views.checkout, name="checkout"),
    path("", views.sale_history, name="sale_history"),
    path("<int:pk>/", views.sale_detail, name="sale_detail"),
    path("<int:pk>/ticket/", views.sale_ticket, name="sale_ticket"),
    path("<int:pk>/ticket.pdf", views.sale_ticket_pdf, name="sale_ticket_pdf"),
    path("<int:pk>/cancelar/", views.sale_cancel, name="sale_cancel"),
]

