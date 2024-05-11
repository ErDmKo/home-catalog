from django.core.management.base import BaseCommand, CommandError
import subprocess


class Command(BaseCommand):
    help = "Build a docker image.tar"

    def handle(self, *args, **options):
        PROJECT_NAME = "home_catalog"

        subprocess.run(["./manage.py", "build"])
        subprocess.run("pwd")
        subprocess.run(
            [
                "ansible-playbook",
                "-i",
                "./ansible/inventory.yaml",
                "./ansible/push.yaml",
            ]
        )
        self.stdout.write(self.style.SUCCESS("Deploy is done"))
