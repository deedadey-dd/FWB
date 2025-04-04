from django.urls import path
from .views import record_contribution, dashboard, manager_dashboard, view_contributions, extra_contributions_view, \
    send_reminder_message, export_contributions, confirm_send_messages, request_benefit, review_benefit_requests, \
    process_benefit_request, accounting_dashboard

urlpatterns = [
    path('record-contribution/', record_contribution, name='record_contribution'),
    path('dashboard/', dashboard, name='dashboard'),
    path("mgt-dashboard/", manager_dashboard, name="manager_dashboard"),
    path("contributions/", view_contributions, name="view_contributions"),
    path("extra-contributions/", extra_contributions_view, name="extra_contributions"),
    path('send_reminder/', send_reminder_message, name='send_reminder_message'),
    path('export-contributions/', export_contributions, name='export_contributions'),
    path('confirm-send-messages/', confirm_send_messages, name='confirm_send_messages'),
    path("request-benefit/", request_benefit, name="request_benefit"),
    path("benefit-requests/", review_benefit_requests, name="review_benefit_requests"),
    path("benefit-requests/<int:request_id>/<str:decision>/", process_benefit_request, name="process_benefit_request"),
    path("accounting-dashboard/", accounting_dashboard, name="accounting_dashboard")
]
