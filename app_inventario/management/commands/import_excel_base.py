from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
import pandas as pd

from app_inventario.views import _import_df_to_locationbase


class Command(BaseCommand):
    help = "Importa el Excel base (PN / Ubicaciones / Descripción) en LocationBase."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Ruta al archivo .xlsx con el master de ubicaciones",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])

        if not file_path.exists():
            raise CommandError(f"Archivo no encontrado: {file_path}")

        self.stdout.write(self.style.NOTICE(f"Leyendo archivo: {file_path}"))

        try:
            # 👇 SIN chunksize: versión compatible con tu pandas
            df = pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            raise CommandError(f"No se pudo leer el Excel: {e}")

        try:
            filas = _import_df_to_locationbase(df)
        except Exception as e:
            raise CommandError(f"Error importando a LocationBase: {e}")

        self.stdout.write(
            self.style.SUCCESS(f"Importación completada. Filas procesadas: {filas}")
        )
