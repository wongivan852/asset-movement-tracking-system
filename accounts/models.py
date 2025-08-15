from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('location_manager', 'Location Manager'),
        ('personnel', 'Personnel'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='personnel')
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_location_manager(self):
        return self.role in ['admin', 'location_manager'] or self.is_superuser
    
    @property
    def is_personnel(self):
        return self.role in ['admin', 'location_manager', 'personnel'] or self.is_superuser
