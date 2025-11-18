from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages

import pandas as pd
from django.db import transaction

from .models import (
    LocationBase,
    CountSession,
    CountDetail,
    ResultSnapshot,  # aunque casi no lo usemos ahora, lo dejamos
)


# ========= Helpers para importar Excel =========

def _norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = (s.replace("á", "a").replace("é", "e").replace("í", "i")
             .replace("ó", "o").replace("ú", "u").replace("ñ", "n"))
    for ch in [" ", "\t", "\n", "-", "_", ".", "/"]:
        s = s.replace(ch, "")
    return s


def _import_df_to_locationbase(df: pd.DataFrame) -> int:
    cols_map = {_norm(c): c for c in df.columns if isinstance(c, str)}

    def pick(cands):
        for k in cands:
            if k in cols_map:
                return cols_map[k]
        return None

    col_pn = pick(["pn", "partnumber", "material", "codigo", "codigomaterial", "materialcode"])
    col_ubi = pick(["ubicaciones", "ubicacion", "location", "ubicacionessap", "ubicacionfisica"])
    col_des = pick(["descripcion", "description", "desc"])

    if not col_pn or not col_ubi:
        raise ValueError(f"Faltan columnas PN o Ubicaciones. Encabezados: {list(df.columns)}")

    if not col_des:
        df["__descripcion__"] = ""
        col_des = "__descripcion__"

    df = df[[col_pn, col_ubi, col_des]].rename(columns={
        col_pn: "pn",
        col_ubi: "ubicacion",
        col_des: "descripcion",
    })

    df["pn"] = df["pn"].astype(str).str.strip()
    df["ubicacion"] = df["ubicacion"].astype(str).str.strip()
    df["descripcion"] = df["descripcion"].astype(str).fillna("").str.strip()

    df = df[(df["pn"] != "") & (df["ubicacion"] != "")]
    df = df.dropna(subset=["pn", "ubicacion"])
    df = df.drop_duplicates(subset=["pn", "ubicacion"], keep="last")

    objs = [
        LocationBase(
            pn=row["pn"],
            ubicacion=row["ubicacion"],
            descripcion=row["descripcion"],
            activo=True,
        )
        for _, row in df.iterrows()
    ]

    with transaction.atomic():
        LocationBase.objects.all().delete()
        LocationBase.objects.bulk_create(objs, batch_size=1000)

    return len(objs)


# ========= Vistas principales =========

def cargar_excel(request):
    """Subir Excel desde la web y actualizar LocationBase."""
    if request.method == "POST" and request.FILES.get("archivo"):
        try:
            df = pd.read_excel(request.FILES["archivo"], engine="openpyxl")
            n = _import_df_to_locationbase(df)
            messages.success(request, f"Archivo importado correctamente. Filas procesadas: {n}.")
            return redirect("buscar_material")
        except Exception as e:
            messages.error(request, f"Error al importar: {e}")
            return redirect("cargar_excel")

    return render(request, "app_inventario/cargar_excel.html")


def buscar_material(request):
    query = request.GET.get("q", "").strip()
    materiales = []

    if query:
        materiales = (
            LocationBase.objects
            .filter(pn__icontains=query, activo=True)
            .values("pn")
            .distinct()
            .order_by("pn")
        )

    return render(request, "app_inventario/buscar_material.html", {
        "query": query,
        "materiales": materiales,
    })


def listado_ubicaciones(request, pn):
    """
    - Si es POST: crea una nueva CountSession para ese PN.
    - Si es GET:
        - Sin ?session= → muestra formulario para crear sesión y listado de sesiones previas.
        - Con ?session=ID → muestra checklist para esa sesión.
    """
    # Crear nueva sesión
    if request.method == "POST":
        operador = request.POST.get("operador", "").strip()
        comentario = request.POST.get("comentario", "").strip()
        if not operador:
            messages.error(request, "Debe ingresar el nombre del operador.")
        else:
            session = CountSession.objects.create(
                pn=pn,
                operador=operador,
                comentario=comentario,
            )
            return redirect(f"{reverse('listado_ubicaciones', args=[pn])}?session={session.id}")

    session_id = request.GET.get("session")
    sesiones_pn = CountSession.objects.filter(pn=pn).order_by("-creado_en")

    session = None
    rows = []
    total = revisadas = 0

    if session_id:
        session = get_object_or_404(CountSession, id=session_id, pn=pn)
        base_ubics = list(LocationBase.objects.filter(pn=pn, activo=True).order_by("ubicacion"))
        detalles = CountDetail.objects.filter(session=session)
        detalles_by_base = {d.base_id: d for d in detalles}

        for b in base_ubics:
            detalle = detalles_by_base.get(b.id)
            rows.append({"base": b, "detalle": detalle})
            if detalle and detalle.revisado:
                revisadas += 1

        total = len(base_ubics)

    porcentaje = round(revisadas / total * 100, 1) if total else 0.0

    return render(request, "app_inventario/listado_ubicaciones.html", {
        "pn": pn,
        "session": session,
        "sesiones_pn": sesiones_pn,
        "rows": rows,
        "total": total,
        "revisadas": revisadas,
        "porcentaje": porcentaje,
    })


def toggle_check(request):
    """Marca/desmarca una ubicación dentro de una sesión."""
    if request.method == "POST":
        session_id = request.POST.get("session_id")
        base_id = request.POST.get("base_id")
        checked = request.POST.get("checked") == "true"

        session = get_object_or_404(CountSession, id=session_id)
        base = get_object_or_404(LocationBase, id=base_id)

        detail, _ = CountDetail.objects.get_or_create(session=session, base=base)
        detail.revisado = checked
        detail.fecha_revision = timezone.now() if checked else None
        detail.save()

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


def historial_pn(request, pn):
    """Historial de sesiones para un PN, con avance calculado."""
    sesiones = CountSession.objects.filter(pn=pn).order_by("-creado_en")

    data = []
    for s in sesiones:
        base_ubics = LocationBase.objects.filter(pn=pn, activo=True)
        total = base_ubics.count()
        revisadas = CountDetail.objects.filter(session=s, revisado=True).count()
        porcentaje = round(revisadas / total * 100, 1) if total else 0.0
        data.append({
            "session": s,
            "total": total,
            "revisadas": revisadas,
            "porcentaje": porcentaje,
        })

    return render(request, "app_inventario/historial_pn.html", {
        "pn": pn,
        "data": data,
    })
