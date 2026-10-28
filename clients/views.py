import json
import urllib.request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client

ARKESEL_API_KEY = "avdSeEnYTghQykI3TndJb3JNCGI"

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
            "sender_id": "AnchorCrest"
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
                print(f"SUCCESS - ARKESEL OTP RESPONSE: {res_body}")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"HTTP ERROR FROM ARKESEL: {e.code} - {error_body}")
        except Exception as e:
            print(f"GENERAL EXCEPTION DURING OTP: {str(e)}")

        messages.info(request, f"A verification code has been sent to {client_data['phone_number']}.")
        return redirect("verify_borrower_otp")

    return render(request, "clients/register_borrower.html")