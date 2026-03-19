from django.contrib import admin
from .models import Loan, Repayment

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_requested', 'status', 'date_applied')
    list_filter = ('status',)

admin.site.register(Repayment)