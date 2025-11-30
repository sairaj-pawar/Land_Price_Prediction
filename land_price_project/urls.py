"""
URLs configuration for land_price_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('land_price_app.urls')),
]