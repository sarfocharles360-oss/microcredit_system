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
    list_display = (
        'id', 
        'client', 
        'get_amount_issued',
        'get_interest_amount', 
        'get_total_payable', 
        'get_duration_weeks', 
        'get_weekly_installment', 
        'get_remaining_balance', 
        'status', 
        'submitted_by'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'client__phone')
    actions = [approve_loans, reject_loans]

    def get_amount_issued(self, obj):
        return f"GHS {obj.amount:.2f}"
    get_amount_issued.short_description = "Amount Issued"

    def get_interest_amount(self, obj):
        return f"GHS {obj.interest_amount:.2f} (20%)"
    get_interest_amount.short_description = "Interest (20%)"

    def get_total_payable(self, obj):
        return f"GHS {obj.total_payable:.2f}"
    get_total_payable.short_description = "Total Payable"

    def get_duration_weeks(self, obj):
        return f"{obj.total_weeks} Weeks"
    get_duration_weeks.short_description = "Duration"

    def get_weekly_installment(self, obj):
        return f"GHS {obj.weekly_installment:.2f} / wk"
    get_weekly_installment.short_description = "Weekly Payment"

    def get_remaining_balance(self, obj):
        return f"GHS {obj.remaining_balance:.2f}"
    get_remaining_balance.short_description = "Balance Due"

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'amount_paid', 'payment_date', 'collected_by')
    list_filter = ('payment_date',)
