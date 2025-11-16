"""
MediLocator Models
commit: feat: add user, medicine, pharmacy, inventory models with indexes
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with phone number and role"""
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
            message="Phone must be: '+999999999'. Up to 15 digits."
        )]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Medicine(models.Model):
    """Medicine master data"""
    name = models.CharField(max_length=255, unique=True, db_index=True)
    generic_name = models.CharField(max_length=255, blank=True)
    common_doses = models.CharField(max_length=255, blank=True)
    searchable_terms = models.TextField(blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name']), models.Index(fields=['generic_name'])]
    
    def __str__(self):
        return self.name


class Pharmacy(models.Model):
    """Pharmacy locations"""
    name = models.CharField(max_length=255, db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=17)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pharmacies')
    verified = models.BooleanField(default=False, db_index=True)
    google_place_id = models.CharField(max_length=255, blank=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-verified', 'name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['verified', 'latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Inventory(models.Model):
    """Pharmacy inventory"""
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='inventory_items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='inventory_items')
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['pharmacy', 'medicine']
        indexes = [
            models.Index(fields=['pharmacy', 'medicine']),
            models.Index(fields=['medicine', 'quantity']),
        ]
    
    def __str__(self):
        return f"{self.medicine.name} @ {self.pharmacy.name}"
    
    @property
    def in_stock(self):
        return self.quantity > 0


class PrescriptionUpload(models.Model):
    """Prescription uploads"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    image = models.ImageField(upload_to='prescriptions/%Y/%m/%d/')
    detected_text = models.TextField(blank=True)
    detected_medicines = models.JSONField(default=list)
    processed = models.BooleanField(default=False, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription by {self.user.username}"
    
    def mark_processed(self):
        self.processed = True
        self.processed_at = timezone.now()
        self.save()


class ChatbotConversation(models.Model):
    """Chatbot conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    session_id = models.CharField(max_length=255, db_index=True)
    messages = models.JSONField(default=list)
    resolved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.session_id}"
    
    def add_message(self, role, content):
        if not isinstance(self.messages, list):
            self.messages = []
        self.messages.append({'role': role, 'content': content, 'timestamp': timezone.now().isoformat()})
        self.save()


class SearchLog(models.Model):
    """Search logs"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='searches')
    medicines = models.JSONField(default=list)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    results_count = models.IntegerField(default=0)
    search_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-search_timestamp']
    
    def __str__(self):
        return f"Search {self.search_timestamp}"


class Feedback(models.Model):
    """User feedback"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"


