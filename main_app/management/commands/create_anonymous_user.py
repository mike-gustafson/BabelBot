from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import secrets

class Command(BaseCommand):
    help = 'Creates an anonymous user for handling anonymous translations'

    def handle(self, *args, **options):
        # Check if anonymous user already exists
        if User.objects.filter(username='anonymous_translator').exists():
            self.stdout.write(self.style.WARNING('Anonymous user already exists'))
            return

        # Generate a secure random password
        password = secrets.token_urlsafe(32)

        # Create the anonymous user
        user = User.objects.create_user(
            username='anonymous_translator',
            password=password,
            email='anonymous@babelbot.com',
            is_active=True,
            is_staff=False
        )

        # Add a flag to mark this as the anonymous user
        user.profile.is_anonymous = True
        user.profile.save()

        self.stdout.write(self.style.SUCCESS('Successfully created anonymous user')) 