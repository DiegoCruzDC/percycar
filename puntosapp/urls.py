from django.contrib import admin
from django.urls import path
from clientes.views import (
    home,
    importar_puntos,
    importar_puntos_preview,
    importar_puntos_confirm,
)

urlpatterns = [
    # Flujo de importación con previsualización
    path('admin/importar_puntos/', importar_puntos, name='importar_puntos'),
    path('admin/importar_puntos/preview/', importar_puntos_preview, name='importar_puntos_preview'),
    path('admin/importar_puntos/confirm/', importar_puntos_confirm, name='importar_puntos_confirm'),

    # Admin Django
    path('admin/', admin.site.urls),

    # Público
    path('', home, name='home'),
]
