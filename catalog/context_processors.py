from .models import CatalogGroup


def catalog_context(request):
    """
    Adds the user's catalog group to the template context if they are
    authenticated and belong to a group.
    """
    return {"current_catalog_group": request.catalog_group}
