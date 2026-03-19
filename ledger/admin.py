from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'status', 'date_created')
    list_filter = ('status', 'transaction_type')
    search_fields = ('user__phone_number', 'reference_code')