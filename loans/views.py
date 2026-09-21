from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import LoanApplication, Repayment
from clients.models import Client
from decimal import Decimal
from django.utils import timezone

@login_required
def loan_list(request):
    loans = LoanApplication.objects.all().order_by('-created_at')
    return render(request, 'loans/loan_list.html', {'loans': loans})

@login_required
def create_loan(request):
    if request.method == 'POST':
        client_id = request.POST.get('client')
        amount_val = request.POST.get('amount') or request.POST.get('amount_requested') or request.POST.get('principal')
        duration_val = request.POST.get('duration_months') or request.POST.get('term_months') or 3

        client = get_object_or_404(Client, id=client_id)

        LoanApplication.objects.create(
            client=client,
            amount=Decimal(amount_val),
            duration_months=int(duration_val),
            submitted_by=request.user,
            status='PENDING'
        )
        return redirect('loan_list')

    clients = Client.objects.all()
    return render(request, 'loans/loan_form.html', {'clients': clients})

@login_required
def record_repayment(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    
    if request.method == 'POST':
        amount_paid_val = Decimal(request.POST.get('amount_paid'))
        payment_date_val = request.POST.get('payment_date') or timezone.now().strftime('%Y-%m-%d')
        user_notes = request.POST.get('notes', '').strip()

        # Create repayment record
        repayment = Repayment.objects.create(
            loan=loan,
            collected_by=request.user,
            amount_paid=amount_paid_val,
            payment_date=payment_date_val,
            notes=user_notes
        )

        # Calculate updated balance after payment
        new_balance = loan.remaining_balance

        # Construct permanent payment SMS text
        client_name = f"{loan.client.first_name} {loan.client.last_name}"
        phone_number = loan.client.phone_number if hasattr(loan.client, 'phone_number') else "N/A"
        
        sms_message = (
            f"Dear {client_name}, payment of GHS {amount_paid_val:.2f} received on {payment_date_val} "
            f"for Loan #{loan.id}. Remaining Balance: GHS {new_balance:.2f}. Thank you! - Anchor Crest"
        )

        # Append auto SMS log into permanent record notes
        permanent_note = f"{user_notes}\n[SMS NOTIFICATION SENT to {phone_number}]: {sms_message}".strip()
        repayment.notes = permanent_note
        repayment.save()

        # Print SMS to console terminal (or integrate SMS gateway provider)
        print(f"\n--- [SMS GATEWAY SIMULATION] ---")
        print(f"TO: {phone_number}")
        print(f"MESSAGE: {sms_message}")
        print(f"--------------------------------\n")

        return redirect('loan_list')

    today_date = timezone.now().strftime('%Y-%m-%d')
    return render(request, 'loans/record_payment.html', {'loan': loan, 'today_date': today_date})

@login_required
def approve_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    if request.user.is_staff or request.user.is_superuser:
        loan.status = 'APPROVED'
        loan.save()
    return redirect('loan_list')
