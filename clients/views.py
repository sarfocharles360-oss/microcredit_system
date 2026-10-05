from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client
from .forms import ClientForm
from .sms_utils import generate_otp, send_otp_sms

def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

import traceback

def client_create(request):
    """Step 1: Admin fills form -> saves temporarily, sends OTP via SMS with error trapping."""
    if request.method == 'POST':
        try:
            form = ClientForm(request.POST, request.FILES)
            if form.is_valid():
                client = form.save()
                phone = form.cleaned_data.get('phone_number')
                otp = generate_otp()
                
                request.session['pending_client_id'] = client.id
                request.session['borrower_otp'] = otp
                
                if send_otp_sms(phone, otp):
                    messages.success(request, f"Verification code sent to {phone}.")
                    return redirect('verify_borrower_otp')
                else:
                    messages.error(request, "Failed to send SMS code. Please verify the phone number.")
                    client.delete()
            else:
                # If form is invalid, re-render with errors
                return render(request, 'clients/client_form.html', {'form': form, 'title': 'Register New Borrower'})
        except Exception as e:
            error_msg = traceback.format_exc()
            print(error_msg)  # Prints to your terminal
            from django.http import HttpResponse
            return HttpResponse(f"<h3>An error occurred:</h3><pre>{error_msg}</pre>", status=500)
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Register New Borrower'})

def verify_borrower_otp(request):
    """Step 2: Admin enters code received on borrower's phone to finalize."""
    if request.method == 'POST':
        user_code = request.POST.get('otp_code')
        session_code = request.session.get('borrower_otp')
        client_id = request.session.get('pending_client_id')

        if session_code and user_code == session_code and client_id:
            # Code is correct -> Clean up session data
            del request.session['borrower_otp']
            del request.session['pending_client_id']
            
            messages.success(request, "Borrower phone number verified and registration completed!")
            return redirect('client_list')
        else:
            messages.error(request, "Invalid verification code. Please try again.")

    return render(request, 'clients/verify_otp.html')

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})