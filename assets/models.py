from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Asset Categories"
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_transit', 'In Transit'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]
    
    # Basic Information
    asset_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='assets')
    
    # Physical Details
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial Information
    purchase_date = models.DateField(blank=True, null=True)
    purchase_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True, 
        null=True
    )
    current_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True, 
        null=True
    )
    
    # Status and Location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    current_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='assets'
    )
    
    # Responsibility
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    primary_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_assets',
        help_text='The primary user of this asset'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Fields
    barcode = models.CharField(max_length=100, blank=True, null=True)
    qr_code = models.CharField(max_length=100, blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['asset_id']
        indexes = [
            models.Index(fields=['asset_id']),
            models.Index(fields=['status']),
            models.Index(fields=['current_location']),
        ]
    
    def __str__(self):
        return f"{self.asset_id} - {self.name}"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def is_in_transit(self):
        return self.status == 'in_transit'

class AssetRemark(models.Model):
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('condition', 'Condition Update'),
        ('movement', 'Movement'),
        ('inspection', 'Inspection'),
        ('general', 'General Note'),
        ('issue', 'Issue/Problem'),
        ('repair', 'Repair'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='remarks')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    remark = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Remark for {self.asset.asset_id} by {self.created_by}"
