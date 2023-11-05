from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("product/", include("product.urls")),
    path("admin/", admin.site.urls),
]