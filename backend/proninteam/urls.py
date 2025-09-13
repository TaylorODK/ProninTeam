"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from proninteam.constants import API_VERSION

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{API_VERSION}/", include("api.urls"), name="api"),
    path(f"api/{API_VERSION}/", include("djoser.urls")),
    path(f"api/{API_VERSION}/", include("djoser.urls.jwt")),
    path(
        f"api/{API_VERSION}/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        f"api/{API_VERSION}/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
]
