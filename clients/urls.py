from django.urls import path
from .views import client_list, client_create, client_detail, verify_borrower_otp

urlpatterns = [
    path('', client_list, name='client_list'),
    path('add/',
    path('create/', views.client_create, name='client_create_alias'), client_create, name='client_create'),
    path('register/', client_create, name='register_borrower'), # Fallback route alias
    path('verify-otp/', verify_borrower_otp, name='verify_borrower_otp'),
    path('<int:pk>/', client_detail, name='client_detail'),
]
