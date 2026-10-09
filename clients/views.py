from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client  # Adjust model import if named Borrower

def create_client(request):
    if request.method == "POST":
        # Process form data
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        id_number = request.POST.get("id_number")
        address = request.POST.get("address")
        ghana_card = request.FILES.get("ghana_card")

        # Save to database
        client = Client.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            id_number=id_number,
            address=address,
            ghana_card=ghana_card if ghana_card else None
        )
        messages.success(request, f"Client {first_name} {last_name} registered successfully!")
        return redirect("/clients/")
        
    return render(request, "clients/register_borrower.html")

def client_list(request):
    clients = Client.objects.all().order_by("-id")
    return render(request, "clients/client_list.html", {"clients": clients})

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, "clients/client_detail.html", {"client": client})

