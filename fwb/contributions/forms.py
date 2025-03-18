from django import forms
from django.contrib.auth import get_user_model
from .models import Contribution

User = get_user_model()


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ["user", "amount", "contribution_type"]

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude is_staff users from the user dropdown
        self.fields["user"].queryset = User.objects.filter(is_staff=False)
