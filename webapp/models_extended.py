"""
Extended Models for MediLocator
This file contains all models needed for the complete application.
Will be integrated into models.py after review.
commit: feat: add medicine, pharmacy, inventory models and migrations
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extended user profile with phone number and role
    One-to-One relationship with User model
    """
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('PHARMACY_OWNER', 'Pharmacy Owner'),
        ('ADMIN', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be in format: '+999999999'. Up to 15 digits."
        )]
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='PATIENT',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Medicine(models.Model):
    """
    Medicine master data with searchable terms
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    generic_name = models.CharField(max_length=255, blank=True)
    common_doses = models.CharField(max_length=255, blank=True, help_text="e.g., 500mg, 10mg/ml")
    searchable_terms = models.TextField(blank=True, help_text="Comma-separated alternate names")
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['generic_name']),
        ]
    
    def __str__(self):
        return self.name


class Pharmacy(models.Model):
    """
    Pharmacy locations with coordinates for KNN search
    """
    name = models.CharField(max_length=255, db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=17)
    latitude = models.FloatField(db_index=True, help_text="Latitude coordinate")
    longitude = models.FloatField(db_index=True, help_text="Longitude coordinate")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pharmacies')
    verified = models.BooleanField(default=False, db_index=True)
    google_place_id = models.CharField(max_length=255, blank=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'
        ordering = ['-verified', 'name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['verified', 'latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Inventory(models.Model):
    """
    Pharmacy inventory linking pharmacies to medicines
    """
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='inventory_items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='inventory_items')
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        unique_together = ['pharmacy', 'medicine']
        indexes = [
            models.Index(fields=['pharmacy', 'medicine']),
            models.Index(fields=['medicine', 'quantity']),
        ]
    
    def __str__(self):
        return f"{self.medicine.name} @ {self.pharmacy.name} ({self.quantity} units)"
    
    @property
    def in_stock(self):
        return self.quantity > 0


class PrescriptionUpload(models.Model):
    """
    Stores uploaded prescription images and detected medicines
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    image = models.ImageField(upload_to='prescriptions/%Y/%m/%d/')
    detected_text = models.TextField(blank=True)
    detected_medicines = models.JSONField(default=list)
    processed = models.BooleanField(default=False, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Prescription Upload'
        verbose_name_plural = 'Prescription Uploads'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
    
    def mark_processed(self):
        self.processed = True
        self.processed_at = timezone.now()
        self.save()


class ChatbotConversation(models.Model):
    """
    Stores chatbot conversations
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    session_id = models.CharField(max_length=255, db_index=True)
    messages = models.JSONField(default=list)
    resolved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chatbot Conversation'
        verbose_name_plural = 'Chatbot Conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        user_display = self.user.username if self.user else f"Anonymous ({self.session_id})"
        return f"Conversation with {user_display}"
    
    def add_message(self, role, content):
        if not isinstance(self.messages, list):
            self.messages = []
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': timezone.now().isoformat()
        })
        self.save()


class SearchLog(models.Model):
    """
    Logs search queries for analytics
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='searches')
    medicines = models.JSONField(default=list)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    results_count = models.IntegerField(default=0)
    search_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Search Log'
        verbose_name_plural = 'Search Logs'
        ordering = ['-search_timestamp']
    
    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"Search by {user_display} at {self.search_timestamp.strftime('%Y-%m-%d %H:%M')}"
