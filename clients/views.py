import random
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client

# Configure your Arkesel API key here or in settings.py
ARKESEL_API_KEY = "YOUR_ARKESEL_API_KEY"

def register_borrower(request):
    if request.method == "POST":
        # 1. Collect all registration data from form
        client_data = {
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "phone_number": request.POST.get("phone_number"),
            "email": request.POST.get("email"),
            "id_number": request.POST.get("id_number"),
            "address": request.POST.get("address"),
        }

        # 2. Generate a 6-digit OTP code
        otp_code = str(random.randint(100000, 999999))

        # 3. Save profile data & OTP code temporarily in the session
        request.session["pending_client_data"] = client_data
        request.session["registration_otp"] = otp_code

        # 4. Send OTP via Arkesel SMS API
        phone = client_data["phone_number"]
        sms_message = f"Your Anchor Crest verification code is {otp_code}."
        
        try:
            # Arkesel SMS Endpoint call
            url = f"https://sms.arkesel.com/sms/api?action=send-sms&api_key={ARKESEL_API_KEY}&to={phone}&from=AnchorCrest&sms={sms_message}"
            requests.get(url, timeout=5)
        except Exception as e:
            print(f"SMS sending error: {e}")

        messages.info(request, f"A verification code has been sent to {phone}.")
        return redirect("verify_borrower_otp")

    return render(request, "clients/register_borrower.html")


def verify_borrower_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp_code")
        saved_otp = request.session.get("registration_otp")
        client_data = request.session.get("pending_client_data")

        if entered_otp and entered_otp == saved_otp and client_data:
            # OTP Verified -> Create the client in the database
            client = Client.objects.create(
                first_name=client_data["first_name"],
                last_name=client_data["last_name"],
                phone_number=client_data["phone_number"],
                email=client_data["email"],
                id_number=client_data["id_number"],
                address=client_data["address"],
            )

            # Clear session data
            del request.session["pending_client_data"]
            del request.session["registration_otp"]

            messages.success(request, f"Client {client.first_name} {client.last_name} successfully verified and registered!")
            return redirect("client_list")
        else:
            messages.error(request, "Invalid or expired verification code. Please try again.")

    return render(request, "clients/verify_otp.html")


def client_list(request):
    clients = Client.objects.all().order_by("-id")
    return render(request, "clients/client_list.html", {"clients": clients})


def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, "clients/client_detail.html", {"client": client})

