from django.core.management.base import BaseCommand, CommandError
from django.utils import autoreload
import subprocess
from esbuild_py import build


class Command(BaseCommand):
    help = "Compile typesctiprt app to static"

    def compile_cmd(self):
        build("./frontend/index.ts", "./catalog/static/catalog/js/bundle.js")

    def handle(self, *args, **options):
        self.compile_cmd()
        self.stdout.write(self.style.SUCCESS("Compile is ready"))
