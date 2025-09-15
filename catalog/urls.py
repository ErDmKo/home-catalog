from django.urls import path, include
from rest_framework import routers
from django.contrib.auth import views as auth_views

from . import views
from . import api_views


app_name = "catalog"

router = routers.DefaultRouter()
router.register(r"item-definitions", api_views.ItemDefinitionViewSet)
router.register(r"catalog-entries", api_views.CatalogEntryViewSet)
router.register(r"groups", api_views.CatalogGroupViewSet)
router.register(r"invitations", api_views.InvitationViewSet, basename="invitation")

urlpatterns = [
    path("", views.CatalogListView.as_view(), name="index"),
    path("create/", views.EntryCreateView.as_view(), name="create"),
    path(
        "create-catalog-group/",
        views.CatalogGroupCreateView.as_view(),
        name="create-catalog-group",
    ),
    path("create-group/", views.ItemGroupCreateView.as_view(), name="create-group"),
    path("api/", include(router.urls)),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path(
        "update/<int:entry_id>/",
        views.UpdateEntryStatusView.as_view(),
        name="update",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="catalog:index"),
        name="logout",
    ),
    path("login/", views.CatalogLoginView.as_view(), name="login"),
]
