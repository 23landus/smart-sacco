from django.db import models
from django.conf import settings
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

class Loan(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('DISBURSED', 'Disbursed (Money Sent)'),
        ('FULLY_PAID', 'Fully Paid'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00) 
    penalty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.00) # 2% Penalty
    duration_months = models.IntegerField(default=12)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_applied = models.DateTimeField(auto_now_add=True)

    @property
    def base_total_payable(self):
        """Calculates Principal + Interest only."""
        interest = (self.amount_requested * self.interest_rate) / 100
        return self.amount_requested + interest

    @property
    def total_repaid(self):
        """Sums only the VERIFIED repayments."""
        return self.repayments.filter(status='VERIFIED').aggregate(
            Sum('amount')
        )['amount__sum'] or 0

    @property
    def due_date(self):
        """Calculates the date the loan must be fully paid."""
        return self.date_applied + timedelta(days=self.duration_months * 30)

    @property
    def is_overdue(self):
        """Checks if the deadline has passed while a balance exists."""
        # Check balance against base amount first to avoid recursion
        base_balance = self.base_total_payable - self.total_repaid
        if base_balance > 0 and timezone.now() > self.due_date:
            return True
        return False

    @property
    def penalty_amount(self):
        """Calculates penalty if the loan is overdue."""
        if self.is_overdue:
            # Penalty is 2% of the base balance remaining
            base_balance = self.base_total_payable - self.total_repaid
            return (base_balance * self.penalty_rate) / 100
        return 0

    @property
    def total_repayable(self):
        """Calculates Principal + Interest + Any Penalties."""
        return self.base_total_payable + self.penalty_amount

    @property
    def remaining_balance(self):
        """Final amount the user owes."""
        return self.total_repayable - self.total_repaid

    @property
    def progress_percentage(self):
        """Calculates progress for the dashboard progress bar."""
        total = self.total_repayable
        if total > 0:
            percent = (self.total_repaid / total) * 100
            return min(percent, 100)
        return 0

    def __str__(self):
        name = getattr(self.user, 'full_name', None) or \
               getattr(self.user, 'phone_number', None) or \
               str(self.user)
        return f"{name} - {self.amount_requested} UGX ({self.status})"

class Repayment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    date_paid = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        name = getattr(self.loan.user, 'full_name', None) or \
               getattr(self.loan.user, 'phone_number', None) or \
               str(self.loan.user)
        return f"Repayment of {self.amount} for {name} ({self.status})"