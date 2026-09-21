from django.db import models
from django.contrib.auth.models import User
from clients.models import Client
from decimal import Decimal
from django.utils import timezone

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.IntegerField(default=3)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_weeks(self):
        return self.duration_months * 4

    @property
    def interest_amount(self):
        return self.amount * (self.interest_rate / Decimal('100.00'))

    @property
    def total_payable(self):
        return self.amount + self.interest_amount

    @property
    def weekly_installment(self):
        weeks = self.total_weeks
        if weeks > 0:
            return self.total_payable / Decimal(weeks)
        return Decimal('0.00')

    @property
    def total_paid(self):
        paid = self.repayments.aggregate(models.Sum('amount_paid'))['amount_paid__sum']
        return paid if paid else Decimal('0.00')

    @property
    def remaining_balance(self):
        return self.total_payable - self.total_paid

    def __str__(self):
        return f"Loan #{self.id} - {self.client} ({self.status})"

class Repayment(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='repayments')
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment GHS {self.amount_paid} for Loan #{self.loan.id}"
