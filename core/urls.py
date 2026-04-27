from django.urls import path

from core import views


urlpatterns = [
    path("", views.sync_center, name="sync_center"),
    path("export/json/", views.export_json, name="export_json"),
    path("export/sales.csv", views.export_sales_csv, name="export_sales_csv"),
    path("import/", views.import_json, name="import_json"),
]

