from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    help = "Formats and lints the code"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Automatically fix linting errors",
        )

    def handle(self, *args, **options):
        self.stdout.write("Running formatter...")
        format_result = subprocess.run(["ruff", "format", "."])
        if format_result.returncode != 0:
            self.stdout.write(self.style.ERROR("Formatting failed."))
            return

        self.stdout.write("Running linter...")
        lint_command = ["ruff", "check", "."]
        if options["fix"]:
            self.stdout.write(self.style.SUCCESS("Autofix is enabled"))
            lint_command.append("--fix")

        lint_result = subprocess.run(lint_command)
        if lint_result.returncode != 0:
            self.stdout.write(self.style.ERROR("Linting failed."))
            return

        self.stdout.write(self.style.SUCCESS("Code is clean."))
