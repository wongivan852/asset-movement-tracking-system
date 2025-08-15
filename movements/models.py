from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Movement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('acknowledged', 'Acknowledged'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Unique tracking number
    tracking_number = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Asset and Movement Details
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='movements')
    from_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='outgoing_movements'
    )
    to_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='incoming_movements'
    )
    
    # Personnel
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='initiated_movements'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_movements'
    )
    
    # Dates and Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expected_arrival_date = models.DateTimeField()
    actual_departure_date = models.DateTimeField(null=True, blank=True)
    actual_arrival_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    reason = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')],
        default='normal'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['expected_arrival_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)
    
    def generate_tracking_number(self):
        """Generate a unique tracking number"""
        prefix = f"MV{timezone.now().year}"
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{unique_id}"
    
    def __str__(self):
        return f"{self.tracking_number}: {self.asset.asset_id} ({self.from_location} → {self.to_location})"
    
    @property
    def is_overdue(self):
        """Check if the movement is overdue"""
        if self.status in ['delivered', 'acknowledged']:
            return False
        return timezone.now() > self.expected_arrival_date
    
    @property
    def days_until_arrival(self):
        """Calculate days until expected arrival"""
        if self.status in ['delivered', 'acknowledged']:
            return 0
        delta = self.expected_arrival_date - timezone.now()
        return delta.days

class MovementAcknowledgement(models.Model):
    movement = models.OneToOneField(Movement, on_delete=models.CASCADE, related_name='acknowledgement')
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    
    # Condition on arrival
    condition_on_arrival = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('damaged', 'Damaged'),
        ],
        default='good'
    )
    
    # Discrepancies
    has_discrepancies = models.BooleanField(default=False)
    discrepancy_notes = models.TextField(blank=True, null=True)
    
    # Additional notes
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Acknowledgement for {self.movement.tracking_number}"

class StockTake(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    stock_take_id = models.CharField(max_length=50, unique=True, db_index=True)
    location = models.ForeignKey('locations.Location', on_delete=models.CASCADE)
    
    # Personnel
    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='conducted_stock_takes'
    )
    supervised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_stock_takes'
    )
    
    # Dates and Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    scheduled_date = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    total_assets_expected = models.IntegerField(default=0)
    total_assets_found = models.IntegerField(default=0)
    discrepancies_found = models.IntegerField(default=0)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['stock_take_id']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.stock_take_id:
            self.stock_take_id = self.generate_stock_take_id()
        super().save(*args, **kwargs)
    
    def generate_stock_take_id(self):
        """Generate a unique stock take ID"""
        prefix = f"ST{timezone.now().year}"
        unique_id = str(uuid.uuid4())[:6].upper()
        return f"{prefix}-{self.location.code}-{unique_id}"
    
    def __str__(self):
        return f"{self.stock_take_id} - {self.location.name}"

class StockTakeItem(models.Model):
    STATUS_CHOICES = [
        ('expected', 'Expected'),
        ('found', 'Found'),
        ('missing', 'Missing'),
        ('unexpected', 'Unexpected Asset Found'),
    ]
    
    stock_take = models.ForeignKey(StockTake, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='expected')
    
    # Condition when found
    condition_found = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('damaged', 'Damaged'),
        ],
        blank=True,
        null=True
    )
    
    # Notes for this specific item
    notes = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['stock_take', 'asset']
        indexes = [
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.stock_take.stock_take_id} - {self.asset.asset_id}"
