from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import subprocess


class Command(BaseCommand):
    help = "Build a docker image.tar"

    def handle(self, *args, **options):
        PROJECT_NAME = "home_catalog"
        call_command("format")
        call_command("compile")
        call_command("collectstatic", "--noinput")
        subprocess.run(["docker", "build", f"-t={PROJECT_NAME}", "."])
        subprocess.run(["docker", "save", PROJECT_NAME, "-o=image.tar"])
        self.stdout.write(self.style.SUCCESS("Build is ready"))
