from django.core.management.base import BaseCommand
import sys
from coverage import Coverage
import pytest


class Command(BaseCommand):
    help = "Run tests with coverage report"

    def add_arguments(self, parser):
        parser.add_argument(
            '--html',
            action='store_true',
            help='Generate HTML coverage report',
        )

    def handle(self, *args, **options):
        # Initialize coverage
        cov = Coverage(
            source=['catalog'],  # Specify the source package to measure
            omit=['*/migrations/*', '*/tests/*']  # Omit certain paths
        )
        cov.start()

        # Configure pytest arguments
        pytest_args = [
            'catalog/tests.py',  # Path to your tests
            '--verbose',
            '-s',  # Show print statements
            '--tb=short',  # Shorter traceback format
        ]

        # Run tests with pytest
        result = pytest.main(pytest_args)
        
        # Stop coverage
        cov.stop()
        cov.save()

        if result != 0:
            self.stderr.write(self.style.ERROR('Tests failed!'))
            sys.exit(result)

        # Generate coverage report
        total = cov.report()
        
        self.stdout.write(
            self.style.SUCCESS(f'Total coverage: {total:.2f}%')
        )

        # Generate HTML report if requested
        if options['html']:
            cov.html_report()
            self.stdout.write(
                self.style.SUCCESS(
                    'HTML coverage report generated in htmlcov/index.html'
                )
            ) 