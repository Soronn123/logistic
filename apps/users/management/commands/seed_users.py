from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed default users'

    def handle(self, *args, **options):
        users_data = [
            {
                'email': 'admin@baikal.ru',
                'username': 'admin@baikal.ru',
                'password': 'admin123',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'Baikal',
                'balance': 100000,
            },
            {
                'email': 'manager@baikal.ru',
                'username': 'manager@baikal.ru',
                'password': 'manager123',
                'role': 'manager',
                'is_staff': True,
                'first_name': 'Manager',
                'last_name': 'Baikal',
                'balance': 50000,
            },
            {
                'email': 'client@baikal.ru',
                'username': 'client@baikal.ru',
                'password': 'client123',
                'role': 'client',
                'first_name': 'Client',
                'last_name': 'Baikal',
                'balance': 10000,
            },
        ]

        for data in users_data:
            email = data['email']
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(**data)
                self.stdout.write(self.style.SUCCESS(f'User created: {email}'))
            else:
                self.stdout.write(f'User already exists: {email}')
