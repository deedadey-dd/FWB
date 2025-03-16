from django import forms
from .models import Contribution


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ["user", "amount", "contribution_type"]

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
