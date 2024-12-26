from django.db import models
from django.core.exceptions import ValidationError
# from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    birth_date = models.DateField()
    phone = models.CharField(max_length=15)

class Room(models.Model):
    name = models.CharField(max_length=100)
    room_type = models.CharField(
        max_length=50,
        choices=[('single', 'Single'), ('double', 'Double'), ('suite', 'Suite')],
    )
    photo = models.ImageField(upload_to='room_photos/', blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    no_of_guests = models.PositiveIntegerField(default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_request = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.check_in and self.check_out:  
            if self.check_out <= self.check_in:
                raise ValidationError("Check-out date must be after check-in date.")
        else:
            raise ValidationError("Both check-in and check-out dates must be provided.")

    def __str__(self):
        return f"{self.user.username} - {self.room.name}"

