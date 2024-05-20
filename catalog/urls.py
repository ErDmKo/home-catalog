from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("update/<int:catalog_item_id>", views.update, name="update"),
]
