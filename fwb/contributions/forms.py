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
        fields = ['benefit_type', 'event_date', 'reason', 'amount_requested']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        benefit_type = cleaned_data.get('benefit_type')
        amount_requested = cleaned_data.get('amount_requested')
        reason = cleaned_data.get('reason')

        if benefit_type == "other":
            if not amount_requested:
                self.add_error('amount_requested', "Amount is required for 'Other' benefit type.")
            if amount_requested and amount_requested <= 0:
                self.add_error('amount_requested', "Amount must be greater than zero.")
            if not reason:
                self.add_error('reason', "Reason is required for 'Other' benefit type.")
        else:
            if amount_requested:
                self.add_error('amount_requested', "Amount should not be set for standard benefit types.")
            if reason:
                self.add_error('reason', "Reason should not be set for standard benefit types.")

        return cleaned_data


class BenefitReviewForm(forms.ModelForm):
    class Meta:
        model = BenefitRequest
        fields = ["amount_requested", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount_requested"].widget.attrs.update({"class": "form-control", "min": "0", "step": "0.01"})
        self.fields["status"].widget.attrs.update({"class": "form-select"})
