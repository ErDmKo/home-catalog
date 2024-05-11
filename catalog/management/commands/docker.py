from django.core.management.base import BaseCommand, CommandError
from subprocess import run, PIPE, STDOUT, Popen
import os


class Command(BaseCommand):
    help = "Runs a docker image.tar localy"

    def handle(self, *args, **options):
        PROJECT_NAME = "home_catalog"
        run(["./manage.py", "build"])
        docker_args = [
            "docker",
            "run",
            "--publish=8000:8000",
            "--rm",
            "--name=home_catalog_run",
            "home_catalog",
        ]
        run(docker_args, stdout=PIPE, bufsize=0)
        self.stdout.write(self.style.SUCCESS(f"Run is finished"))
