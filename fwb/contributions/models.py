from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model


User = get_user_model()


class Contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_contributed = models.DateField(default=now)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='recorded_contributions'
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

    class Meta:
        unique_together = ("user", "year", "month")

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year} - {self.amount}"


class ExtraContribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="extra_contributions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    date_contributed = models.DateField(default=now)

    def __str__(self):
        return f"{self.user.username} - Extra Contribution: {self.amount}"
