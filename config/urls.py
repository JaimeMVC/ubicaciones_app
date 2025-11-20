from django.contrib import admin
from django.urls import path
from app_inventario import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Buscador principal
    path("", views.buscar_material, name="buscar_material"),

    # Cargar / actualizar Excel base
    path("cargar-excel/", views.cargar_excel, name="cargar_excel"),

    # Trabajo sobre PN
    path("material/<str:pn>/", views.listado_ubicaciones, name="listado_ubicaciones"),
    path("material/<str:pn>/historial/", views.historial_pn, name="historial_pn"),

    # Informes de sesión
    path("sesion/<int:session_id>/informe/", views.informe_sesion, name="informe_sesion"),
    path(
        "sesion/<int:session_id>/exportar-csv/",
        views.exportar_sesion_csv,
        name="exportar_sesion_csv",
    ),

    # NUEVOS endpoints (Ajax + PDF)
    path("api/toggle-check/", views.toggle_check, name="toggle_check"),
    path(
        "api/actualizar-cantidad/",
        views.actualizar_cantidad,
        name="actualizar_cantidad",
    ),
    path(
        "material/<str:pn>/pdf/",
        views.exportar_listado_pdf,
        name="exportar_listado_pdf",
    ),
]
