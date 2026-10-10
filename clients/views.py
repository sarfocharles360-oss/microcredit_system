import json
import urllib.request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client

ARKESEL_API_KEY = "a2t3SXBzU1FvcmpuRVJreXBTdGU="

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
        request.session["pending_client_data"] = client_data

        formatted_phone = format_ghana_phone(client_data["phone_number"])

        payload = {
            "expiry": 5,
            "length": 6,
            "medium": "sms",
            "number": formatted_phone,
            "sender_id": "Arkesel"
        }

        try:
            req = urllib.request.Request(
                "https://sms.arkesel.com/api/otp/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "api-key": ARKESEL_API_KEY,
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                print(f"ARNKESEL OTP API RESPONSE: {res_body}")
        except Exception as e:
            print(f"ARKESEL OTP API ERROR: {e}")

        messages.info(request, f"A verification code has been sent to {client_data['phone_number']}.")
        return redirect("verify_borrower_otp")

    return render(request, "clients/register_borrower.html")

def verify_borrower_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp_code", "").strip()
        client_data = request.session.get("pending_client_data")
        formatted_phone = format_ghana_phone(client_data["phone_number"]) if client_data else ""

        payload = {
            "confirm": entered_otp,
            "number": formatted_phone
        }

        try:
            req = urllib.request.Request(
                "https://sms.arkesel.com/api/otp/verify",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "api-key": ARKESEL_API_KEY,
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                
                # Check if verification succeeded according to Arkesel's response
                if res_body.get("status") == "success" and client_data:
                    client = Client.objects.create(
                        first_name=client_data["first_name"],
                        last_name=client_data["last_name"],
                        phone_number=client_data["phone_number"],
                        email=client_data["email"],
                        id_number=client_data["id_number"],
                        address=client_data["address"],
                    )
                    request.session.pop("pending_client_data", None)
                    messages.success(request, f"Client {client.first_name} verified successfully!")
                    return redirect("client_list")
        except Exception as e:
            print(f"VERIFY OTP ERROR: {e}")

        messages.error(request, "Invalid or expired verification code.")

    return render(request, "clients/verify_otp.html")

def client_list(request):
    clients = Client.objects.all().order_by("-id")
    return render(request, "clients/client_list.html", {"clients": clients})

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, "clients/client_detail.html", {"client": client})