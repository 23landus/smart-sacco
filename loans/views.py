import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.utils import timezone

from ledger.models import Transaction
from .models import Loan, Repayment
from .forms import LoanApplicationForm, LoanRepaymentForm

# --- MEMBER VIEWS ---

@login_required
def apply_loan(request):
    """Allows members to apply for loans based on 3x their verified savings."""
    
    # RECTIFICATION: Ensure we only block if a loan is actually active.
    # Rejected or Closed loans should NOT block a new application.
    active_loan_exists = Loan.objects.filter(
        user=request.user, 
        status__in=['PENDING', 'APPROVED', 'DISBURSED']
    ).exists()

    if active_loan_exists:
        messages.error(request, "Access Denied! You must clear your current active loan before applying for a new one.")
        return redirect('dashboard')

    savings = Transaction.objects.filter(
        user=request.user, 
        status='VERIFIED'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    limit = savings * 3

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan_amount = form.cleaned_data['amount_requested']
            
            if loan_amount > limit:
                messages.error(request, f"Access Denied! Your max loan limit is {limit} UGX based on your savings.")
            else:
                loan = form.save(commit=False)
                loan.user = request.user
                loan.save()
                messages.success(request, "Loan application submitted successfully!")
                return redirect('dashboard')
    else:
        form = LoanApplicationForm()

    return render(request, 'loans/apply_loan.html', {'form': form, 'limit': limit})

@login_required
def log_repayment(request):
    """Allows members to log a payment for the Treasurer to verify."""
    if request.method == 'POST':
        form = LoanRepaymentForm(request.user, request.POST)
        if form.is_valid():
            repayment = form.save(commit=False)
            repayment.status = 'PENDING' 
            repayment.save()
            
            messages.info(request, f"Repayment of {repayment.amount} UGX submitted for verification.")
            return redirect('dashboard')
    else:
        form = LoanRepaymentForm(request.user)
        
    return render(request, 'loans/log_repayment.html', {'form': form})

@login_required
def loan_statement(request, loan_id):
    """Detailed breakdown of a loan: Principal, Interest, Penalties, and Payments."""
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)
    repayments = loan.repayments.filter(status='VERIFIED').order_by('-date_paid')
    
    context = {
        'loan': loan,
        'repayments': repayments,
        'interest_amount': (loan.amount_requested * loan.interest_rate) / 100,
    }
    return render(request, 'loans/loan_statement.html', context)


# --- TREASURER (STAFF) VIEWS ---

@staff_member_required
def treasurer_dashboard(request):
    """Master view for SACCO management to track liquidity and loan health."""
    User = get_user_model()
    all_loans = Loan.objects.all()
    
    total_savings = Transaction.objects.filter(status='VERIFIED').aggregate(Sum('amount'))['amount__sum'] or 0
    disbursed_loans = all_loans.filter(status='DISBURSED')
    total_principal_out = disbursed_loans.aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0
    cash_at_hand = total_savings - total_principal_out
    
    total_interest_expected = sum(
        (loan.penalty_amount or 0) + ((loan.amount_requested * loan.interest_rate) / 100) 
        for loan in disbursed_loans
    )

    members = User.objects.all().order_by('full_name')

    context = {
        'total_savings': total_savings,
        'cash_at_hand': cash_at_hand,
        'total_principal': total_principal_out,
        'total_interest': total_interest_expected,
        'pending_loans': all_loans.filter(status='PENDING').order_by('-date_applied'),
        # RECTIFICATION: Use date_applied for sorting to avoid FieldError
        'active_loans_all': all_loans.filter(status__in=['APPROVED', 'DISBURSED']).order_by('-date_applied'),
        'loan_history': all_loans.filter(status__in=['REJECTED', 'CLOSED']).order_by('-date_applied'),
        'members': members,
        'overdue_count': len([l for l in disbursed_loans if l.is_overdue]),
    }
    return render(request, 'loans/treasurer_dashboard.html', context)

@staff_member_required
def approve_loan(request, loan_id):
    """Processes Approval or Rejection of loan applications."""
    loan = get_object_or_404(Loan, id=loan_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            loan.status = 'APPROVED'
            messages.success(request, f"Loan for {loan.user} approved!")
        elif action == 'reject':
            loan.status = 'REJECTED'
            messages.warning(request, f"Loan for {loan.user} rejected.")
        loan.save()
    return redirect('treasurer_dashboard')

@staff_member_required
def disburse_loan(request, loan_id):
    """Finalizes the loan by marking it as disbursed and activating interest."""
    loan = get_object_or_404(Loan, id=loan_id)
    if request.method == 'POST' and loan.status == 'APPROVED':
        loan.status = 'DISBURSED'
        loan.save()
        messages.success(request, f"Loan for {loan.user} marked as DISBURSED. Interest is now active.")
    return redirect('treasurer_dashboard')

@staff_member_required
def export_sacco_report(request):
    """Generates an Excel-compatible CSV report based on date range."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Transactions still use date_created
    transactions = Transaction.objects.filter(status='VERIFIED').order_by('-date_created')
    if start_date and end_date:
        transactions = transactions.filter(date_created__range=[start_date, end_date])

    response = HttpResponse(content_type='text/csv')
    filename = f"SACCO_Financial_Report_{timezone.now().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Member Name', 'Phone', 'Transaction Type', 'Amount (UGX)', 'Status'])

    for tx in transactions:
        writer.writerow([
            tx.date_created.strftime("%Y-%m-%d %H:%M"),
            tx.user.full_name or "N/A",
            tx.user.phone_number,
            tx.get_transaction_type_display() if hasattr(tx, 'get_transaction_type_display') else tx.transaction_type,
            tx.amount,
            tx.status
        ])

    return response