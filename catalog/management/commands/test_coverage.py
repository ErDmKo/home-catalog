from django.core.management.base import BaseCommand
import sys
from coverage import Coverage
import pytest


class Command(BaseCommand):
    help = "Run tests with coverage report"

    def add_arguments(self, parser):
        parser.add_argument(
            "--html",
            action="store_true",
            help="Generate HTML coverage report",
        )
        parser.add_argument(
            "test_labels",
            nargs="*",
            help="Test labels (e.g., catalog.tests.test_mixins.QueryParamsMixinTests.test_build_item_query_with_to_buy)",
        )

    def convert_django_label_to_pytest_path(self, label):
        """
        Convert Django-style test label to pytest path.

        Handles patterns like:
        - catalog.tests.test_mixins
        - catalog.tests.test_mixins.QueryParamsMixinTests
        - catalog.tests.test_mixins.QueryParamsMixinTests.test_method
        - catalog.tests.unit.test_file
        - catalog.tests.unit.models.test_file.TestClass.test_method
        - app/tests/test_file.py
        """
        if not label:
            return "catalog/tests"

        # If it's already a file path, return as is
        if "/" in label:
            return label

        # Convert dots to path components
        parts = label.split(".")

        if parts[0] == "catalog" and parts[1] == "tests":
            path_parts = ["catalog", "tests"]

            # Find the test file part
            test_file_index = -1
            for i, part in enumerate(parts[2:], 2):
                if part.startswith("test_"):
                    test_file_index = i
                    break

            if test_file_index == -1:
                # No test file found, treat last part as file
                path_parts.extend(parts[2:-1])  # Add any middle directories
                path_parts.append(f"{parts[-1]}.py")
            else:
                # Add directories before test file
                path_parts.extend(parts[2:test_file_index])

                # Add test file
                path_parts.append(f"{parts[test_file_index]}.py")

                # Add class and method if present
                remaining_parts = parts[test_file_index + 1 :]
                if remaining_parts:
                    path_parts[-1] += "::" + "::".join(remaining_parts)
        else:
            # Default to catalog/tests
            path_parts = ["catalog", "tests", f"{parts[-1]}.py"]

        return "/".join(path_parts)

    def handle(self, *args, **options):
        # Start coverage monitoring
        cov = Coverage(source=["catalog"], omit=["*/tests/*", "*/migrations/*"])
        cov.start()

        # Convert test labels to pytest paths
        test_labels = options.get("test_labels", [])
        if not test_labels:
            test_args = ["catalog/tests"]
        else:
            test_args = [
                self.convert_django_label_to_pytest_path(label) for label in test_labels
            ]

        # Add pytest options
        test_args.extend(["-v"])  # Add verbosity

        # Run tests
        result = pytest.main(test_args)

        if result != 0:
            self.stdout.write(self.style.ERROR("Tests failed!"))
            sys.exit(result)

        # Generate coverage report
        cov.stop()
        total = cov.report()

        self.stdout.write(self.style.SUCCESS(f"Total coverage: {total:.2f}%"))

        # Generate HTML report if requested
        if options["html"]:
            cov.html_report()
            self.stdout.write(
                self.style.SUCCESS(
                    "HTML coverage report generated in htmlcov/index.html"
                )
            )
