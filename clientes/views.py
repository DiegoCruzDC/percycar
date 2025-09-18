import csv, io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from .models import Cliente

import pandas as pd  # para Excel/CSV flexible

# ---------- PÁGINA PÚBLICA ----------
def home(request):
    q = request.GET.get('dni')
    resultado = Cliente.objects.filter(dni=q).first() if q else None
    demo_products = [
        {"icon":"⛽","name":"Galón de gasolina","points":50},
        {"icon":"🧽","name":"Lavado express","points":120},
        {"icon":"☕","name":"Café Americano","points":30},
        {"icon":"🛢️","name":"Aceite sintético","points":300},
        {"icon":"🧴","name":"Aromatizante","points":40},
        {"icon":"🧤","name":"Guantes","points":60},
    ]
    products = demo_products + demo_products
    return render(request, 'home.html', {'resultado': resultado, 'products': products})


# ---------- IMPORTACIÓN CON PREVIEW ----------
def _norm(s):
    return (s or "").strip().lower()

def _read_to_df(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith('.csv'):
        data = uploaded_file.read().decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(data))
        rows = list(reader)
        if not rows:
            raise ValueError("CSV vacío.")
        return pd.DataFrame(rows[1:], columns=rows[0])
    elif name.endswith('.xls') or name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file, engine='openpyxl')
    else:
        raise ValueError("Formato no soportado. Usa .csv, .xls o .xlsx.")

def _detect_columns(df):
    cols = { _norm(c): c for c in df.columns }
    dni_col     = next((cols[k] for k in ['dni','documento','dni_cliente','identificacion','rut'] if k in cols), None)
    nombre_col  = next((cols[k] for k in ['nombre','nombres','cliente','nombre_completo','full_name'] if k in cols), None)
    puntos_col  = next((cols[k] for k in ['puntos','pts','points','score'] if k in cols), None)
    return dni_col, nombre_col, puntos_col

@staff_member_required
def importar_puntos(request):
    """Página de formulario: aquí subes y mandas a preview."""
    return render(request, 'importar.html')

@staff_member_required
@require_http_methods(["POST"])
def importar_puntos_preview(request):
    """Lee el archivo, valida y MUESTRA qué pasará. No guarda todavía."""
    f = request.FILES.get('archivo')
    if not f:
        messages.error(request, "Sube un archivo (.csv, .xls o .xlsx).")
        return redirect('importar_puntos')

    try:
        df = _read_to_df(f)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo: {e}")
        return redirect('importar_puntos')

    dni_col, nombre_col, puntos_col = _detect_columns(df)
    if not dni_col or not puntos_col:
        det = ", ".join(list(df.columns))
        messages.error(request, f"Encabezados inválidos. Necesito al menos 'dni' y 'puntos'. Detectados: {det}")
        return redirect('importar_puntos')

    # Analizar filas
    preview_rows = []
    resumen = {
        "total": 0,
        "nuevos": 0,
        "sumas": 0,                # DNIs existentes a los que se sumará puntos
        "nombre_difiere": 0,       # DNI existe, nombre cargado ≠ nombre en BD
        "invalidos": 0,            # filas sin DNI o sin puntos válidos
    }

    for _, row in df.iterrows():
        dni_txt = str(row.get(dni_col) or "").strip()
        if not dni_txt:
            resumen["invalidos"] += 1
            continue

        nombre_txt = str(row.get(nombre_col) or "").strip() if nombre_col else ""
        try:
            puntos_val = int(float(row.get(puntos_col)))
        except Exception:
            resumen["invalidos"] += 1
            continue

        cli = Cliente.objects.filter(dni=dni_txt).first()
        estado = "nuevo" if not cli else "sumará"
        nombre_ok = True

        if cli:
            # si existe y viene un nombre distinto (y no vacío), lo marcamos
            if nombre_txt and (nombre_txt.strip() != (cli.nombre or "").strip()):
                nombre_ok = False
                estado = "sumará (NOMBRE DIFERENTE)"

        preview_rows.append({
            "dni": dni_txt,
            "nombre": nombre_txt,
            "puntos_a_sumar": puntos_val,
            "existe": bool(cli),
            "nombre_actual": (cli.nombre if cli else ""),
            "puntos_actuales": (cli.puntos if cli else 0),
            "estado": estado,
            "nombre_ok": nombre_ok,
        })

        resumen["total"] += 1
        if not cli:
            resumen["nuevos"] += 1
        else:
            resumen["sumas"] += 1
            if not nombre_ok:
                resumen["nombre_difiere"] += 1

    # Guardamos en sesión para confirmar
    request.session["import_preview_rows"] = preview_rows
    request.session["import_preview_cols"] = [dni_col, nombre_col, puntos_col]

    return render(request, "importar_preview.html", {
        "preview": True,
        "resumen": resumen,
        "rows": preview_rows[:300],  # mostramos hasta 300 en tabla (para no explotar el template)
        "total_rows": len(preview_rows),
    })

@staff_member_required
@require_http_methods(["POST"])
def importar_puntos_confirm(request):
    """Aplica lo analizado: SUMA puntos. Actualiza nombre solo si no está vacío."""
    preview_rows = request.session.get("import_preview_rows")
    if not preview_rows:
        messages.error(request, "No hay datos para importar. Vuelve a subir el archivo.")
        return redirect('importar_puntos')

    del request.session["import_preview_rows"]
    request.session.pop("import_preview_cols", None)

    importados = 0
    nuevos = 0
    actualizados = 0

    with transaction.atomic():
        for r in preview_rows:
            dni = r["dni"]
            nombre = r["nombre"]
            puntos = r["puntos_a_sumar"]

            cli, created = Cliente.objects.get_or_create(
                dni=dni,
                defaults={"nombre": nombre or "", "puntos": 0}
            )
            if nombre:
                cli.nombre = nombre
            cli.puntos = (cli.puntos or 0) + puntos
            cli.save()

            importados += 1
            if created: nuevos += 1
            else: actualizados += 1

    messages.success(request,
        f"✅ Importados: {importados} (nuevos: {nuevos}, actualizados: {actualizados}). "
        f"Los puntos se han SUMADO a los existentes."
    )
    return redirect('importar_puntos')
