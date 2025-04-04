from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils.translation import gettext_lazy as _


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


# BENEFITS AND EXPENSES

class BenefitType(models.TextChoices):
    WEDDING = "wedding", _("Wedding Benefit")
    FUNERAL = "funeral", _("Funeral Benefit")
    CHILDBIRTH = "childbirth", _("Childbirth Benefit")


class WelfareBenefit(models.Model):
    """Tracks welfare benefits received by users."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="welfare_benefits"
    )  # The recipient
    benefit_type = models.CharField(max_length=20, choices=BenefitType.choices)
    amount_awarded = models.DecimalField(max_digits=10, decimal_places=2)
    extra_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Transportation, logistics, etc.
    date_awarded = models.DateField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="benefits_recorded"
    )

    def total_expense(self):
        return self.amount_awarded + self.extra_costs  # Total spent on benefit

    def clean(self):
        if self.amount_awarded <= Decimal("0"):
            raise ValidationError({"amount_awarded": "The benefit amount must be greater than zero."})
        if self.extra_costs < Decimal("0"):
            raise ValidationError({"extra_costs": "Extra costs cannot be negative."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.benefit_type} Benefit: {self.amount_awarded}"


class BenefitRequestStatus(models.TextChoices):
    PENDING = "Pending", _("Pending")
    ACCEPTED = "Accepted", _("Accepted")
    DENIED = "Denied", _("Denied")


class BenefitRequest(models.Model):
    """Users request a benefit, and admins approve or deny it."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="benefit_requests")
    benefit_type = models.CharField(
        max_length=20,
        choices=[
            ("wedding", "Wedding Benefit"),
            ("funeral", "Funeral Benefit"),
            ("childbirth", "Childbirth Benefit"),
            ("other", "Other"),
        ],
    )
    event_date = models.DateField()  # Date of the event (past or future)
    reason = models.TextField(blank=True, null=True)  # Required only for "Other"
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=BenefitRequestStatus.choices, default=BenefitRequestStatus.PENDING
    )
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="benefit_reviews")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount_requested is None:
            raise ValidationError({"amount_requested": "This field is required."})

        # Ensure amount_requested is treated as a Decimal
        amount = Decimal(str(self.amount_requested))

        if amount <= Decimal("0"):
            raise ValidationError({"amount_requested": "The requested amount must be greater than zero."})

        if self.benefit_type == "other" and not self.reason:
            raise ValidationError({"reason": "Reason is required when selecting 'Other' benefit type."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} requested {self.benefit_type} - {self.amount_requested}"


# EXPENSES

class ExpenseCategory(models.TextChoices):
    BENEFIT = "Benefit", _("Benefit-Related Expense")
    GENERAL = "General", _("General Welfare Expense")
    ADMIN = "Admin", _("Administrative Expense")


class Expense(models.Model):
    """Tracks expenses made by the welfare group."""
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses"
    )  # If expense is user-specific; otherwise, it's 'All'
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=ExpenseCategory.choices, default=ExpenseCategory.GENERAL)
    date = models.DateField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="expenses_recorded"
    )  # Only staff should record expenses

    def clean(self):
        if self.amount <= Decimal("0"):
            raise ValidationError({"amount": "The expense amount must be greater than zero."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        recipient = self.user.username if self.user else "All"
        return f"{self.category} Expense - {recipient}: {self.amount}"



