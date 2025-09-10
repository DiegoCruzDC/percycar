from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Crea o actualiza el superusuario desde variables de entorno."

    def handle(self, *args, **kwargs):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )

        # Asegurar permisos y contraseña siempre
        user.is_staff = True
        user.is_superuser = True
        user.email = email
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{username}' listo (created={created})."
        ))
