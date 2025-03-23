from django.urls import path
from .views import record_contribution, dashboard, manager_dashboard, view_contributions, extra_contributions_view

urlpatterns = [
    path('record-contribution/', record_contribution, name='record_contribution'),
    path('dashboard/', dashboard, name='dashboard'),
    path("mgt-dashboard/", manager_dashboard, name="manager_dashboard"),
    path("contributions/", view_contributions, name="view_contributions"),
    path("extra-contributions/", extra_contributions_view, name="extra_contributions"),
]
