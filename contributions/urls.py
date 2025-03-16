from django.urls import path
from .views import record_contribution

urlpatterns = [
    path("record-contribution/", record_contribution, name="record_contribution"),
]
