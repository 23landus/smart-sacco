from django import forms
from .models import Transaction

class DepositRequestForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'reference_code', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Enter Amount'}),
            'reference_code': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Bank/Mobile Money Ref'}),
            'notes': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
        }