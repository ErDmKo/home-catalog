from django.urls import path, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers

from . import views
from . import api_views


router = routers.DefaultRouter()
router.register(r"items", api_views.CatalogItemViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", include(router.urls)),
    path("item/add", login_required(views.ItemCreateView.as_view()), name="item-add"),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("update/<int:catalog_item_id>", views.update, name="update"),
]
