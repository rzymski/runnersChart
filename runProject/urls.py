from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include('runChart.urls')),
    path("admin/", admin.site.urls),
    path("chart/", include('runChart.urls')),
]
