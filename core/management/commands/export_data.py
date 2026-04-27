import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from core.services.sync_service import export_database_json, export_sales_csv_response


class Command(BaseCommand):
    help = "Exporta datos locales del POS en JSON o CSV."

    def add_arguments(self, parser):
        parser.add_argument("--format", choices=["json", "csv"], default="json")
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        output = Path(options["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        if options["format"] == "json":
            output.write_text(json.dumps(export_database_json(), indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            response = export_sales_csv_response()
            output.write_text(response.content.decode("utf-8"), encoding="utf-8")
        if not output.exists():
            raise CommandError("No se pudo crear el archivo de exportacion.")
        self.stdout.write(self.style.SUCCESS(f"Exportado: {output}"))

