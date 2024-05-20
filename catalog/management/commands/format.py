from django.core.management.base import BaseCommand, CommandError
import subprocess


class Command(BaseCommand):
    help = "Build a docker image.tar"

    def handle(self, *args, **options):
        subprocess.run(["ruff", "format"])
