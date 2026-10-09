from django.urls import path
from . import views

urlpatterns = [
    path("", views.client_list, name="client_list"),
    path("add/", views.register_borrower, name="client_create"),
    path("register/", views.register_borrower, name="register_borrower"),
    path("verify-otp/", views.verify_borrower_otp, name="verify_borrower_otp"),
    path("<int:pk>/", views.client_detail, name="client_detail"),
]