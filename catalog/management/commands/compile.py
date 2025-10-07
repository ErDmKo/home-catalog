from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from esbuild_py import build

BASE_DIR = Path(settings.BASE_DIR)
ENTRY_POINT = BASE_DIR / "frontend" / "index.ts"
OUTFILE = BASE_DIR / "catalog" / "static" / "catalog" / "js" / "bundle.js"


class Command(BaseCommand):
    help = "Compile typescript app to static"

    def compile_cmd(self):
        compile_result = build(
            entry_points=[str(ENTRY_POINT)],
            outfile=str(OUTFILE),
        )
        if compile_result.get("errors"):
            self.stdout.write(self.style.ERROR("Compile error:"))
            for error in compile_result["errors"]:
                self.stdout.write(f'- {error["text"]}')
            raise CommandError("TypeScript compilation failed.")

    def handle(self, *args, **options):
        self.compile_cmd()
        self.stdout.write(self.style.SUCCESS("Compile is ready"))
