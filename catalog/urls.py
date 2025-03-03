from django.urls import path, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from django.contrib.auth import views as auth_views

from . import views
from . import api_views


app_name = "catalog"

router = routers.DefaultRouter()
router.register(r"items", api_views.CatalogItemViewSet)

urlpatterns = [
    path("", views.CatalogListView.as_view(), name="index"),
    path("create/", views.ItemCreateView.as_view(), name="create"),
    path("api/", include(router.urls)),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path(
        "update/<int:catalog_item_id>/",
        views.UpdateItemStatusView.as_view(),
        name="update",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="catalog:index"),
        name="logout",
    ),
    path("login/", views.CatalogLoginView.as_view(), name="login"),
]
