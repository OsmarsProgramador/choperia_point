# choperia/urls.py
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuario/', include('usuario.urls')),
    path('estoque/', include('estoque.urls')),
    path('produto/', include('produto.urls')),
    path('mesa/', include('mesa.urls')),
    path('empresa/', include('empresa.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

