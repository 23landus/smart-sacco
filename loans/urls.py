from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_loan, name='apply_loan'),
    path('repay/', views.log_repayment, name='log_repayment'),
    path('statement/<int:loan_id>/', views.loan_statement, name='loan_statement'),
    path('treasurer/', views.treasurer_dashboard, name='treasurer_dashboard'),
    path('approve/<int:loan_id>/', views.approve_loan, name='approve_loan'),
    path('disburse/<int:loan_id>/', views.disburse_loan, name='disburse_loan'),
    path('treasurer/export-report/', views.export_sacco_report, name='export_report'),
]