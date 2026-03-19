from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction
from loans.models import Loan
from .forms import DepositRequestForm

@login_required
def log_deposit(request):
    if request.method == 'POST':
        form = DepositRequestForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.transaction_type = 'SAVING'
            transaction.status = 'PENDING'
            transaction.save()
            return redirect('dashboard')
    else:
        form = DepositRequestForm()
    return render(request, 'ledger/log_deposit.html', {'form': form})

@login_required
def dashboard(request):
    # 1. Sum of only VERIFIED savings
    savings = Transaction.objects.filter(
        user=request.user, 
        transaction_type='SAVING', 
        status='VERIFIED'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # 2. Get all ledger transactions (These use date_created)
    transactions = Transaction.objects.filter(user=request.user).order_by('-date_created')

    # 3. FIX: Changed date_created to date_applied for Loans
    active_loans = Loan.objects.filter(
        user=request.user,
        status__in=['PENDING', 'APPROVED', 'DISBURSED']
    ).order_by('-date_applied')

    # 4. FIX: Changed date_created to date_applied here too
    loan_history = Loan.objects.filter(
        user=request.user, 
        status__in=['REJECTED', 'CLOSED']
    ).order_by('-date_applied')

    context = {
        'user': request.user,
        'verified_savings': savings,
        'active_loans': active_loans,
        'loan_history': loan_history,
        'transactions': transactions,
    }
    return render(request, 'ledger/dashboard.html', context)