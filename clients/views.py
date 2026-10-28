import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Client

def format_ghana_phone(phone):
    if not phone:
        return ""
    phone = str(phone).strip().replace(" ", "").replace("-", "").replace("+", "")
    if phone.startswith("0") and len(phone) == 10:
        return "233" + phone[1:]
    return phone

def client_list(request):
    clients = Client.objects.all()
    return render(request, "clients/client_list.html", {"clients": clients})

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, "clients/client_detail.html", {"client": client})

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

            # Generate secure 6-digit OTP
            generated_otp = str(random.randint(100000, 999999))
            request.session["pending_otp"] = generated_otp

            # Email the OTP to the admin
            subject = "AnchorCrest Admin Alert: Borrower Verification Code"
            message = (
                f"A new borrower registration is pending verification.\n\n"
                f"Client Name: {client_data['first_name']} {client_data['last_name']}\n"
                f"Phone Number: {client_data['phone_number']}\n\n"
                f"Verification OTP Code: {generated_otp}\n\n"
                f"Please enter this code on the verification page to complete registration."
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['sarfocharles360@gmail.com'],
                    fail_silently=False,
                )
                messages.info(request, f"A verification code has been sent to the administrator email.")
            except Exception as mail_err:
                print(f"EMAIL SEND ERROR: {str(mail_err)}")
                messages.error(request, "Failed to send verification email. Please check server logs.")
                return redirect("register_borrower")

            return redirect("verify_borrower_otp")

        except Exception as e:
            print(f"CRITICAL VIEW ERROR: {str(e)}")
            messages.error(request, "An error occurred during registration. Please try again.")
            return redirect("register_borrower")

    return render(request, "clients/register_borrower.html")

def verify_borrower_otp(request):
    pending_data = request.session.get("pending_client_data")
    expected_otp = request.session.get("pending_otp")

    if not pending_data:
        messages.error(request, "No pending registration found. Please register again.")
        return redirect("register_borrower")

    if request.method == "POST":
        entered_otp = request.POST.get("otp_code", "").strip()

        if entered_otp == expected_otp:
            Client.objects.create(
                first_name=pending_data.get("first_name"),
                last_name=pending_data.get("last_name"),
                phone_number=pending_data.get("phone_number"),
                email=pending_data.get("email"),
                id_number=pending_data.get("id_number"),
                address=pending_data.get("address"),
            )
            if "pending_client_data" in request.session:
                del request.session["pending_client_data"]
            if "pending_otp" in request.session:
                del request.session["pending_otp"]

            messages.success(request, "Borrower registered and verified successfully!")
            return redirect("client_list")
        else:
            messages.error(request, "Invalid verification code. Please check your email and try again.")

    return render(request, "clients/verify_otp.html", {"phone_number": pending_data.get("phone_number")})