from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('catalog/admin/', admin.site.urls),
    path('catalog/', include('catalog.urls'))
]
