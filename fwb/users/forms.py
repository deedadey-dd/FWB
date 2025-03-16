from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator

from .models import CustomUser, Contact, Child

User = get_user_model()

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
)


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': '+1234567890'})
    )
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'other_names', 'phone_number',
                  'date_of_birth', 'hometown', 'residence',]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'residence': forms.Textarea(attrs={'rows': 3}),
        }


class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'other_names', 'phone_number',
                  'date_of_birth', 'hometown', 'residence',]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'relationship', 'phone_number']


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'date_of_birth', 'phone_number']


class LoginForm(forms.Form):
    identifier = forms.CharField(label='Username, Email or Phone',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }
