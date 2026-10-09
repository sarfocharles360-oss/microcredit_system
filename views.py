from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Client, Loan

def home(request):
    return render(request, 'home.html')

@login_required
@staff_member_required(login_url='login')
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'client_list.html', {'clients': clients})

@login_required
@staff_member_required(login_url='login')
def loan_list(request):
    loans = Loan.objects.all()
    return render(request, 'loan_list.html', {'loans': loans})

@login_required
@staff_member_required(login_url='login')
def client_create(request):
    # Add your client creation view logic here
    pass

import random
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User

def send_otp_sms(phone_number, otp_code):
    formatted_phone = phone_number.replace("+", "").strip()
    message = f"Your Anchor Crest verification code is: {otp_code}. Valid for 5 minutes."
    url = "https://sms.arkesel.com/api/v2/sms/send"
    headers = {"api-key": getattr(settings, "ARKESEL_API_KEY", "")}
    payload = {"sender": "AnchorCrest", "message": message, "recipients": [formatted_phone]}
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"SMS sending error: {e}")
        return False

def verify_otp_view(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp_code")
        session_otp = request.session.get("otp_code")
        if entered_otp and entered_otp == session_otp:
            user_id = request.session.get("user_id_for_verification")
            if user_id:
                user = User.objects.get(id=user_id)
                login(request, user)
                del request.session["otp_code"]
                del request.session["user_id_for_verification"]
                return redirect("loans_list")
        messages.error(request, "Invalid or expired OTP code. Please try again.")
    return render(request, "registration/verify_otp.html")

