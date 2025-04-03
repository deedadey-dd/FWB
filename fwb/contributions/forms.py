from django import forms
from django.contrib.auth import get_user_model
from .models import Contribution, ExtraContribution, BenefitRequest

User = get_user_model()


# class ContributionForm(forms.ModelForm):
#
#     previous_reason = forms.ModelChoiceField(
#         queryset=ExtraContribution.objects.none(),
#         required=False,
#         widget=forms.Select(attrs={"class": "form-control"}),
#         label="Select Previous Reason"
#     )
#
#     new_reason = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter new reason"}),
#         label="New Reason"
#     )
#
#     class Meta:
#         model = Contribution
#         fields = ["user", "amount", "contribution_type"]
#
#     def clean_amount(self):
#         amount = self.cleaned_data["amount"]
#         if amount <= 0:
#             raise forms.ValidationError("Amount must be greater than zero.")
#         return amount
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Exclude is_staff users from the user dropdown
#         self.fields["user"].queryset = User.objects.filter(is_staff=False)
#         # Populate previous reasons
#         self.fields["previous_reason"].queryset = ExtraContribution.objects.distinct()


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_date"].widget.attrs.update({"type": "date"})
        self.fields["reason"].widget.attrs.update({"placeholder": "Explain why you need this benefit."})
