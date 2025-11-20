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

    # SSO Integration Fields
    sso_user = models.BooleanField(default=False, help_text="User authenticated via SSO")
    sso_provider = models.CharField(max_length=50, blank=True, null=True, help_text="SSO provider name (SAML, OAuth, LDAP)")
    sso_id = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text="Unique identifier from SSO provider")
    last_sso_login = models.DateTimeField(blank=True, null=True, help_text="Last successful SSO login")
    
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
