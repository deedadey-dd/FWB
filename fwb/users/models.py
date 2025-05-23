from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    residence = models.CharField(max_length=250, blank=True, null=True)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    phone_number = PhoneNumberField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    next_of_kin = models.ForeignKey(
        'Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_as_next_of_kin'
    )
    hometown = models.CharField(max_length=100, null=True, blank=True)
    profile_complete = models.BooleanField(default=False)

    def check_profile_completion(self):
        required_fields = [
            self.residence,
            self.date_of_birth,
            self.next_of_kin,
            self.hometown,
            self.contacts.exists()
        ]
        return all(required_fields)

    def __str__(self):
        other_names_display = self.other_names or ""
        return f'{self.first_name} {other_names_display} {self.last_name}'


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


# class Child(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=CASCADE, related_name='Children')
#     name = models.CharField(max_length=150,)
#     date_of_birth = models.DateField()
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
