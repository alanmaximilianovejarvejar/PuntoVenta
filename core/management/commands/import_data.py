import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.services.sync_service import import_database_json


class Command(BaseCommand):
    help = "Importa datos JSON generados por export_data."

    def add_arguments(self, parser):
        parser.add_argument("file")
        parser.add_argument("--user", default="admin")

    def handle(self, *args, **options):
        path = Path(options["file"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        User = get_user_model()
        user = User.objects.filter(username=options["user"]).first()
        summary = import_database_json(payload, user)
        self.stdout.write(self.style.SUCCESS(summary))

