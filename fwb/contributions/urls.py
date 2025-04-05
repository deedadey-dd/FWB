from django.urls import path
from .views import record_contribution, dashboard, manager_dashboard, view_contributions, extra_contributions_view, \
    send_reminder_message, export_contributions, confirm_send_messages, request_benefit, review_benefit_requests, \
    accounting_dashboard, delete_benefit_request, edit_benefit_request, fulfill_benefit_request, all_benefit_requests, \
    benefit_request_detail

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
    path("accounting-dashboard/", accounting_dashboard, name="accounting_dashboard"),
    path("review-benefit-requests/", review_benefit_requests, name="review_benefit_requests"),
    path('delete-benefit/<int:pk>/', delete_benefit_request, name='delete_benefit'),
    path('benefit/<int:pk>/edit/', edit_benefit_request, name='edit_benefit'),
    path('benefits/<int:request_id>/fulfill/', fulfill_benefit_request, name='fulfill_benefit_request'),
    path('benefits/all/', all_benefit_requests, name='all_benefit_requests'),
    path('benefits/<int:pk>/', benefit_request_detail, name='benefit_request_detail'),
    # path('benefits/<int:pk>/status/<str:status>/', update_benefit_status, name='update_benefit_status'),
    path('benefits/<int:pk>/fulfill/', fulfill_benefit_request, name='fulfill_benefit_request'),
]
