from django.urls import path
from .views import record_contribution, dashboard

urlpatterns = [
    path('record-contribution/', record_contribution, name='record_contribution'),
    path('dashboard/', dashboard, name='dashboard'),
]
