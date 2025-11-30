from django.core.management.base import BaseCommand
from task_api.models import Employee
from django.db import IntegrityError

class Command(BaseCommand):
    help = "Create initial superadmin employee with id=1 if not present"

    def handle(self, *args, **kwargs):
        email = "superadmin@example.com"
        phone = "123456789"
        try:
            obj, created = Employee.objects.get_or_create(
                email=email,
                defaults={
                    'name': 'superadmin',
                    'phone': phone,
                    'role': 'superadmin',
                }
            )
            if created:
                # try set id to 1 if possible (only works if DB allows; otherwise it's created with auto id)
                # If you need guarantee id=1, ensure you run this on a fresh DB before any Employee created.
                obj.set_password("superadminpassword")  # change as needed
                obj.save()
                self.stdout.write(self.style.SUCCESS('Superadmin created.'))
            else:
                self.stdout.write('Superadmin already exists.')
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Could not create superadmin: {e}'))
