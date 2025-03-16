from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE


class CustomUser(AbstractUser):
    other_names = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    next_of_kin = models.CharField(max_length=100, null=True, blank=True)
    hometown = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.other_names} {self.last_name}'


class Contact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Next of Kin', 'Next of Kin'),
        ('Child', 'Child'),
        ('Emergency', 'Emergency'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=CASCADE, related_name='contacts')
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)

    def __str__(self):
        return f'{self.name} ({self.relationship}) - {self.user.first_name}'


class Child(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=CASCADE, related_name='Children')
    name = models.CharField(max_length=150,)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)

