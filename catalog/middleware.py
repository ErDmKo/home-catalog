from .models import CatalogGroup


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
            # Attach the catalog group to the request for easy access.
            request.catalog_group = CatalogGroup.objects.filter(
                owners=request.user
            ).first()

        response = self.get_response(request)
        return response
