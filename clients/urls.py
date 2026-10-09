from django.urls import path
from . import views

urlpatterns = [
    path("", views.client_list, name="client_list"),
    path("add/", views.create_client, name="client_create"),
    path("create/", views.create_client, name="client_create_alias"),
    path("register/", views.register_borrower, name="register_borrower"),
    path("verify-otp/", views.verify_borrower_otp, name="verify_borrower_otp"),
    path("<int:pk>/", views.client_detail, name="client_detail"),
]

