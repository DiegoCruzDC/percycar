import csv, io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from .models import Cliente

# Productos demo para la barra inferior
DEMO_PRODUCTS = [
    {"icon":"⛽","name":"Galón de gasolina","points":50},
    {"icon":"🧽","name":"Lavado express","points":120},
    {"icon":"☕","name":"Café Americano","points":30},
    {"icon":"🛢️","name":"Aceite sintético","points":300},
    {"icon":"🧴","name":"Aromatizante","points":40},
    {"icon":"🧤","name":"Guantes","points":60},
]
def get_products():
    return DEMO_PRODUCTS + DEMO_PRODUCTS  # para el marquee

# Página pública (consulta DNI)
def home(request):
    q = request.GET.get('dni')
    resultado = Cliente.objects.filter(dni=q).first() if q else None
    return render(request, 'home.html', {'resultado':resultado, 'products':get_products()})

# Admin: formulario
@staff_member_required
def importar_puntos(request):
    return render(request, 'importar.html')

# Admin: subir CSV
@staff_member_required
@require_http_methods(["POST"])
def importar_puntos_subir(request):
    f = request.FILES.get('archivo')
    if not f or not f.name.lower().endswith('.csv'):
        messages.error(request, "Sube un archivo .csv")
        return redirect('importar_puntos')

    data = f.read().decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(data))
    count = 0
    with transaction.atomic():
        for row in reader:
            dni = (row.get('dni') or '').strip()
            if not dni: continue
            nombre = (row.get('nombre') or '').strip()
            puntos = int((row.get('puntos') or 0))
            Cliente.objects.update_or_create(
                dni=dni,
                defaults={'nombre': nombre, 'puntos': puntos}
            )
            count += 1
    messages.success(request, f"Importados/actualizados: {count}")
    return redirect('importar_puntos')
