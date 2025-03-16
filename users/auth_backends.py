from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check if username is provided
        if username is None or password is None:
            return None

        # Try logging in with username, email, or phone_number
        user = None
        try:
            user = User.objects.get(models.Q(username=username) | models.Q(email=username) | models.Q(phone_number=username))
        except User.DoesNotExist:
            return None

        if user and user.check_password(password):
            return user
        return None