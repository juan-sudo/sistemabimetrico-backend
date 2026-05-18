from django.apps import apps
from django.core.management.color import no_style
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reset DB sequences (useful after loaddata with explicit PKs)."

    def handle(self, *args, **options):
        sql = connection.ops.sequence_reset_sql(no_style(), apps.get_models())
        if not sql:
            self.stdout.write(self.style.WARNING("No sequences to reset."))
            return

        with connection.cursor() as cursor:
            for statement in sql:
                cursor.execute(statement)

        self.stdout.write(self.style.SUCCESS("Sequences reset."))
