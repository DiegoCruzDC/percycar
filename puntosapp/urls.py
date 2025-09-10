from django.contrib import admin
from django.urls import path
from clientes.views import home, importar_puntos, importar_puntos_subir

urlpatterns = [
    # --- Rutas personalizadas bajo /admin/ (deben ir ANTES) ---
    path('admin/importar_puntos/', importar_puntos, name='importar_puntos'),
    path('admin/importar_puntos/subir/', importar_puntos_subir, name='importar_puntos_subir'),

    # --- Admin de Django ---
    path('admin/', admin.site.urls),

    # --- Página pública ---
    path('', home, name='home'),
]
