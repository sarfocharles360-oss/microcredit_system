import secrets
import urllib.request
import urllib.parse
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client

ARKESEL_API_KEY = "YOUR_COPIED_ARKESEL_KEY"

def format_ghana_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")
    if phone.startswith("0") and len(phone) == 10:
        return "233" + phone[1:]
    return phone

def register_borrower(request):
    if request.method == "POST":
        client_data = {
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "phone_number": request.POST.get("phone_number", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "id_number": request.POST.get("id_number", "").strip(),
            "address": request.POST.get("address", "").strip(),
        }

        otp_code = str(secrets.randbelow(900000) + 100000)
        request.session["pending_client_data"] = client_data
        request.session["registration_otp"] = otp_code

        raw_phone = client_data["phone_number"]
        formatted_phone = format_ghana_phone(raw_phone)
        sms_message = f"Your Anchor Crest verification code is {otp_code}."

        if raw_phone and ARKESEL_API_KEY != "YOUR_ARKESEL_API_KEY":
            try:
                params = urllib.parse.urlencode({
                    "action": "send-sms",
                    "api_key": ARKESEL_API_KEY,
                    "to": formatted_phone,
                    "sender": "Arkesel",
                    "sms": sms_message
                })
                url = f"https://sms.arkesel.com/sms/api?{params}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_body = response.read().decode("utf-8")
                    print(f"ARKESEL SMS RESPONSE: {res_body}")
            except Exception as e:
                print(f"ARKESEL SMS ERROR: {e}")

        messages.info(request, f"A verification code has been sent to {raw_phone}.")
        return redirect("verify_borrower_otp")

    return render(request, "clients/register_borrower.html")


def verify_borrower_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp_code", "").strip()
        saved_otp = request.session.get("registration_otp")
        client_data = request.session.get("pending_client_data")

        if entered_otp and entered_otp == saved_otp and client_data:
            client = Client.objects.create(
                first_name=client_data["first_name"],
                last_name=client_data["last_name"],
                phone_number=client_data["phone_number"],
                email=client_data["email"],
                id_number=client_data["id_number"],
                address=client_data["address"],
            )

            request.session.pop("pending_client_data", None)
            request.session.pop("registration_otp", None)

            messages.success(request, f"Client {client.first_name} {client.last_name} verified successfully!")
            return redirect("client_list")
        else:
            messages.error(request, "Invalid or expired verification code.")

    return render(request, "clients/verify_otp.html")


def client_list(request):
    clients = Client.objects.all().order_by("-id")
    return render(request, "clients/client_list.html", {"clients": clients})


def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, "clients/client_detail.html", {"client": client})

