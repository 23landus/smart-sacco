from django.db import models
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Transaction

class LedgerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            phone_number="+256700111222",
            full_name="Alice Member",
            password="testpassword"
        )

    def test_verified_savings_only(self):
        # Create one verified saving
        Transaction.objects.create(
            user=self.user, amount=5000, 
            transaction_type='SAVING', status='VERIFIED', 
            reference_code="REF1"
        )
        # Create one pending saving
        Transaction.objects.create(
            user=self.user, amount=2000, 
            transaction_type='SAVING', status='PENDING', 
            reference_code="REF2"
        )
        
        # Logic: We only want to sum verified amounts
        verified_total = Transaction.objects.filter(
            user=self.user, status='VERIFIED'
        ).aggregate(models.Sum('amount'))['amount__sum']
        
        self.assertEqual(verified_total, 5000)