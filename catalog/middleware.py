from .models import CatalogGroup
from django.shortcuts import redirect
from django.urls import reverse


class CatalogGroupMiddleware:
    """
    This middleware attaches the current user's catalog group to the request
    object. This avoids repeated database queries in views and templates.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.catalog_group = None
        if request.user.is_authenticated:
            request.catalog_group = CatalogGroup.objects.filter(
                owners=request.user
            ).first()

        response = self.get_response(request)
        return response


class RedirectToCreateCatalogMiddleware:
    """
    Redirects users who do not have a catalog group to the catalog creation
    page. This ensures that new users are guided to the first necessary step.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_superuser
            and not request.catalog_group
        ):
            # Prevent redirect loops by checking the current path.
            allowed_paths = [
                reverse("catalog:create-catalog-group"),
                reverse("catalog:logout"),
            ]
            if request.path not in allowed_paths and "api" not in request.path:
                return redirect("catalog:create-catalog-group")

        response = self.get_response(request)
        return response
