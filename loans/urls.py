from django.urls import path
from . import views

urlpatterns = [
    path('', views.loan_list, name='loan_list'),
    path('new/', views.create_loan, name='create_loan'),
    path('<int:loan_id>/pay/', views.record_repayment, name='record_repayment'),
    path('<int:loan_id>/approve/', views.approve_loan, name='approve_loan'),
]
