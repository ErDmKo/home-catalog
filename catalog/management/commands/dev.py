from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Compile static files and run the development server'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Compiling static files...'))
        call_command('compile')
        self.stdout.write(self.style.SUCCESS('Starting development server...'))
        call_command('runserver')
