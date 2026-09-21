from django.contrib import admin
from .models import LoanApplication, Repayment

@admin.action(description='Approve selected loan applications')
def approve_loans(modeladmin, request, queryset):
    queryset.update(status='APPROVED')

@admin.action(description='Reject selected loan applications')
def reject_loans(modeladmin, request, queryset):
    queryset.update(status='REJECTED')

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'amount', 'status', 'created_at', 'submitted_by')
    list_filter = ('status', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'client__phone')
    actions = [approve_loans, reject_loans]

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'amount_paid', 'payment_date')
    list_filter = ('payment_date',)
