from django.urls import path

from fwb.fwb.urls import urlpatterns
from .views import register, update_profile, add_child, add_contact, user_login, user_logout

urlpatterns = [
    path("login/", user_login, name="login"),
    path('register/', register, name='register'),
    path('profile/update/', update_profile, name='update_profile'),
    path('contacts/add', add_contact, name='add_contact'),
    path('children/add/', add_child, name='add_child'),
    path("logout/", user_logout, name="logout"),
]