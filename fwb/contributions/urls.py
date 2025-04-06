from django.urls import path
from .views import record_contribution, dashboard, manager_dashboard, view_contributions, extra_contributions_view, \
    send_reminder_message, export_contributions, confirm_send_messages, request_benefit, review_benefit_requests, \
    accounting_dashboard, delete_benefit_request, edit_benefit_request, fulfill_benefit_request, all_benefit_requests, \
    benefit_request_detail, financial_dashboard, expenses_dashboard

urlpatterns = [
    path('record-contribution/', record_contribution, name='record_contribution'),
    path('dashboard/', dashboard, name='dashboard'),
    path("mgt-dashboard/", manager_dashboard, name="manager_dashboard"),
    path("contributions/", view_contributions, name="view_contributions"),
    path("extra-contributions/", extra_contributions_view, name="extra_contributions"),
    path('send_reminder/', send_reminder_message, name='send_reminder_message'),
    path('export-contributions/', export_contributions, name='export_contributions'),
    path('confirm-send-messages/', confirm_send_messages, name='confirm_send_messages'),
    path("benefits/request-benefit/", request_benefit, name="request_benefit"),
    path("accounting-dashboard/", accounting_dashboard, name="accounting_dashboard"),
    path("benefits/review-requests/", review_benefit_requests, name="review_benefit_requests"),
    path('benefits/delete-benefit/<int:pk>/', delete_benefit_request, name='delete_benefit'),
    path('benefits/<int:pk>/edit/', edit_benefit_request, name='edit_benefit'),
    path('benefits/<int:request_id>/fulfill/', fulfill_benefit_request, name='fulfill_benefit_request'),
    path('benefits/all/', all_benefit_requests, name='all_benefit_requests'),
    path('benefits/<int:pk>/', benefit_request_detail, name='benefit_request_detail'),
    path('benefits/<int:pk>/fulfill/', fulfill_benefit_request, name='fulfill_benefit_request'),
    path('financial-dashboard/', financial_dashboard, name='financial_dashboard'),
    path('financial-dashboard/all/', financial_dashboard, name='financial_dashboard_all'),
    path('expenses-dashboard/', expenses_dashboard, name='expenses_dashboard'),
    path('expenses-dashboard/all/', expenses_dashboard, name='expenses_dashboard_all'),
]
