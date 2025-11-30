from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

ROLE_CHOICES = (
    ('employee', 'Employee'),
    ('admin', 'Admin'),
    ('superadmin', 'Superadmin'),
)

class EmployeeManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            # create user w/o usable password (they will register later)
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'employee')
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        # This is not used for your superadmin (we create superadmin via management command),
        # but implement for completeness.
        extra_fields.setdefault('role', 'superadmin')
        user = self._create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Employee(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # used by Django admin (not needed for API)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = EmployeeManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return f"{self.id} - {self.email} ({self.role})"

# append below Employee model

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, related_name='tasks', on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.id} -> {self.employee.email} [{self.status}]"

class TaskEditLog(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, related_name='edit_logs', on_delete=models.CASCADE)
    edited_by = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    old_description = models.TextField(blank=True)
    old_status = models.CharField(max_length=20, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.id} for Task {self.task.id} at {self.edited_at}"
