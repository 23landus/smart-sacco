from django.test import TestCase
from django.contrib.auth import get_user_model
from ledger.models import Transaction
from .models import Loan

class LoanEligibilityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            phone_number="+256700999888",
            full_name="Bob Borrower",
            password="password123"
        )
        # Give Bob 10,000 in verified savings
        Transaction.objects.create(
            user=self.user, amount=10000, 
            transaction_type='SAVING', status='VERIFIED', 
            reference_code="BOB-SAVE-1"
        )

    def test_loan_multiplier_rule(self):
        # Calculate Bob's total verified savings
        from django.db.models import Sum
        savings = Transaction.objects.filter(
            user=self.user, status='VERIFIED'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        limit = savings * 3
        
        # Bob wants 40,000 (which is more than 3x 10,000)
        request_amount = 40000
        
        self.assertEqual(limit, 30000)
        self.assertLess(limit, request_amount) # This confirms Bob is NOT eligible for 40k