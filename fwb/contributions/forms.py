from django import forms
from django.contrib.auth import get_user_model
from .models import Contribution, ExtraContribution, BenefitRequest
from decimal import Decimal

User = get_user_model()


class ContributionForm(forms.ModelForm):
    previous_reason = forms.ChoiceField(
        choices=[], required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Select Previous Reason"
    )

    new_reason = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter new reason"}),
        label="New Reason"
    )

    class Meta:
        model = Contribution
        fields = ["user", "amount", "contribution_type"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Exclude staff users from the user dropdown
        self.fields["user"].queryset = User.objects.filter(is_staff=False)

        # Populate previous reasons only for the selected user
        # if user:
        previous_reasons = ExtraContribution.objects.values_list("reason", flat=True).distinct()
        self.fields["previous_reason"].choices = [("", "Select a reason")] + [(r, r) for r in previous_reasons]


class BenefitRequestForm(forms.ModelForm):
    class Meta:
        model = BenefitRequest
        fields = ["benefit_type", "event_date", "amount_requested", "reason"]

    def clean_amount_requested(self):
        cleaned_data = self.cleaned_data
        benefit_type = cleaned_data.get("benefit_type")
        amount_requested = cleaned_data.get("amount_requested")

        if benefit_type == "other":
            if amount_requested is None or amount_requested <= 0:
                raise forms.ValidationError("You must enter a valid amount when selecting 'Other'.")
        else:
            return 0  # Automatically set amount to 0 for non-"Other" benefits

        return amount_requested

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make `event_date` a date picker
        self.fields["event_date"].widget.attrs.update({"type": "date"})

        # Add placeholder for reason field
        self.fields["reason"].widget.attrs.update({"placeholder": "Explain why you need this benefit."})

        # Hide `amount_requested` unless benefit type is "Other"
        if self.instance and self.instance.benefit_type != "other":
            self.fields.pop("amount_requested", None)  # Remove the field


class BenefitReviewForm(forms.ModelForm):
    class Meta:
        model = BenefitRequest
        fields = ["amount_requested", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount_requested"].widget.attrs.update({"class": "form-control", "min": "0", "step": "0.01"})
        self.fields["status"].widget.attrs.update({"class": "form-select"})
