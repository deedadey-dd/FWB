from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from decimal import Decimal


User = get_user_model()


class ContributionSetting(models.Model):
    year = models.IntegerField(unique=True)  # Unique year
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Monthly contribution amount
    set_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.year} - {self.amount}"


class Contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_contributed = models.DateField(default=now)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='contributions_recorded'
    )
    contribution_type = models.CharField(
        max_length=10, choices=[('monthly', 'Monthly'), ('extra', 'Extra')], default='monthly'
    )

    class Meta:
        ordering = ['-date_contributed']

    def __str__(self):
        return f'{self.user.username} - {self.amount} on {self.date_contributed}'


class MonthlyContribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_contributions")
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.amount is not None and self.amount <= Decimal("0"):  # Convert to Decimal
            raise ValidationError({"amount": "The contribution amount must be greater than zero."})

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("user", "year", "month")

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year} - {self.amount}"


class ExtraContribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="extra_contributions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    date_contributed = models.DateField(default=now)

    def clean(self):
        if self.amount is not None and self.amount <= Decimal("0"):  # Convert to Decimal
            raise ValidationError({"amount": "The contribution amount must be greater than zero."})

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Extra Contribution: {self.amount}"


class ContributionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contribution_records")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_type = models.CharField(max_length=20, choices=[("monthly", "Monthly"), ("extra", "Extra")])
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name="contribution_record")
    recorded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount is not None and self.amount <= Decimal("0"):  # Convert to Decimal
            raise ValidationError({"amount": "The contribution amount must be greater than zero."})

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} contributed {self.amount} on {self.recorded_at}"
