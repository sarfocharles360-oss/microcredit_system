import json
import urllib.request
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client

ARKESEL_API_KEY = "avdSeEnYTghQykI3TndJb3JNCGI"

def format_ghana_phone(phone):
    if not phone:
        return ""
    phone = str(phone).strip().replace(" ", "").replace("-", "").replace("+", "")
    if phone.startswith("0") and len(phone) == 10:
        return "233" + phone[1:]
    return phone

def register_borrower(request):
    if request.method == "POST":
        try:
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
                "sender_id": "AnchorCrest"
            }

            # Attempt Arkesel API call safely
            req = urllib.request.Request(
                "https://sms.arkesel.com/api/otp/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "api-key": ARKESEL_API_KEY,
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    print(f"OTP SUCCESS: {res_body}")
            except Exception as net_err:
                print(f"Network restriction/blocked by PythonAnywhere: {net_err}")

            messages.info(request, f"A verification code has been sent to {client_data['phone_number']}.")
            return redirect("verify_borrower_otp")

        except Exception as e:
            print(f"CRITICAL VIEW ERROR: {str(e)}")
            messages.error(request, "An error occurred during registration. Please try again.")
            return redirect("register_borrower")

    return render(request, "clients/register_borrower.html")

def client_list(request):
    clients = Client.objects.all()
    return render(request, "clients/client_list.html", {"clients": clients})