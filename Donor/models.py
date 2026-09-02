import datetime
from django.db import models

# Create your models here.

class Donor(models.Model):
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100, unique=True)
    last_donation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.email

    @property
    def days_since_donation(self):
        if self.last_donation_date:
            return (datetime.date.today() - self.last_donation_date).days
        return None

    @property
    def days_remaining(self):
        if self.days_since_donation is not None:
            remaining = 90 - self.days_since_donation
            return remaining if remaining > 0 else 0
        return 0

    @property
    def is_available(self):
        if self.last_donation_date is None:
            return True
        return self.days_since_donation >= 90

    @property
    def status_text(self):
        if self.is_available:
            return "Available"
        return f"Cannot Donate ({self.days_remaining} days left)"

class AdminCredential(models.Model):
    username = models.CharField(max_length=100, default='admin')
    password = models.CharField(max_length=100, default='admin')

    def __str__(self):
        return self.username