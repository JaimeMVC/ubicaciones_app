from django.core.management.base import BaseCommand, CommandError
from app_inventario.views import _import_excel_stream  # lo vamos a definir abajo


class Command(BaseCommand):
    help = "Importa el Excel base de ubicaciones (PN / Ubicación / Descripción)"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str, help="Ruta al archivo .xlsx")

    def handle(self, *args, **options):
        filepath = options["filepath"]
        try:
            with open(filepath, "rb") as f:
                n = _import_excel_stream(f)
        except FileNotFoundError:
            raise CommandError(f"No se encontró el archivo: {filepath}")

        self.stdout.write(self.style.SUCCESS(
            f"Importación finalizada. Filas procesadas: {n}"
        ))
