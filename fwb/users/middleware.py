from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.user.is_authenticated and
                not request.user.profile_complete and
                request.path not in [reverse('profile'), reverse('logout')]):
            if not any("complete your profile" in str(message) for message in messages.get_messages(request)):
                messages.error(request, "Please complete your profile to access all features.")
            # return redirect('profile')

        return self.get_response(request)