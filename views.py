from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Client, Loan

def home(request):
    return render(request, 'home.html')

@login_required
@staff_member_required(login_url='login')
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'client_list.html', {'clients': clients})

@login_required
@staff_member_required(login_url='login')
def loan_list(request):
    loans = Loan.objects.all()
    return render(request, 'loan_list.html', {'loans': loans})

@login_required
@staff_member_required(login_url='login')
def client_create(request):
    # Add your client creation view logic here
    pass
