from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess


class Command(BaseCommand):
    help = "Build a docker image.tar"

    def handle(self, *args, **options):
        call_command("build")
        subprocess.run(
            [
                "ansible-playbook",
                "-i",
                "./ansible/inventory.yaml",
                "./ansible/push.yaml",
            ]
        )
        self.stdout.write(self.style.SUCCESS("Deploy is done"))
