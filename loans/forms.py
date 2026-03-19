from django import forms
from .models import Repayment, Loan

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount_requested', 'duration_months']
        widgets = {
            'amount_requested': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'Enter amount (e.g. 50000)'
            }),
            'duration_months': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'Duration in months'
            }),
        }

class LoanRepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['loan', 'amount', 'notes']
        widgets = {
            'loan': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'How much are you paying?'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'Reference number or payment notes',
                'rows': 3
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super(LoanRepaymentForm, self).__init__(*args, **kwargs)
        # BUG FIX: Filter for 'DISBURSED' instead of 'APPROVED'
        # A member can only repay a loan that they have actually received.
        self.fields['loan'].queryset = Loan.objects.filter(user=user, status='DISBURSED')
        self.fields['loan'].empty_label = "active loan"
        
        # Optional: Make the dropdown display more useful information
        self.fields['loan'].label_from_instance = lambda obj: f"Loan: {obj.amount_requested} UGX (ID: {obj.id})"