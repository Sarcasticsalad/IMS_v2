from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Product, Customer

def index(request):
    return HttpResponse("Welcome to the Inventory Management System.")

def product_list(request):
    products = Product.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "ims_app/products/product_list.html", {"products": products})

def product_detail(request, sku):
    try:
        product = Product.objects.get(sku=sku, is_active=True)
    except Product.DoesNotExist:
        raise Http404("Product not found.")
    return render(request, "ims_app/products/product_detail.html", {"product": product})

def customer_list(request):
    customers = Customer.objects.order_by("name")
    return render(request, "ims_app/customers/customer_list.html", {"customers": customers})

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, "ims_app/customers/customer_detail.html", {"customer": customer})


