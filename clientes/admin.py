from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('dni','nombre','puntos','actualizado')
    search_fields = ('dni','nombre')

# Branding del admin
admin.site.site_header = "PERCYCAR — Admin"
admin.site.site_title  = "PERCYCAR | Admin"
admin.site.index_title = "Panel principal"
