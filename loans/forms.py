from django import forms
from .models import Loan, Repayment

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['client', 'product', 'loan_number', 'principal_amount', 'interest_rate', 'duration_months']

class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['receipt_number', 'amount_paid', 'payment_method']