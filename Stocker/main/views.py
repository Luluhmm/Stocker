from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from inventory.models import Product, Supplier, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum,Count
import json
from datetime import date, timedelta

# Create your views here.

def landing_view(request):
    return render(request, "main/landing.html")

@login_required
def dashboard_view(request):
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_categories = Category.objects.count()
    low_stock = Product.objects.filter(stock_quantity__lt=10).count()
    total_stock = Product.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0
    recent_products = Product.objects.order_by('-id')[:5]
    
    category_data = Category.objects.annotate(product_count=Count('product'))
    labels = json.dumps([cat.name for cat in category_data])
    data = json.dumps([cat.product_count for cat in category_data])
    
    expiring_soon = Product.objects.filter(
    expiry_date__isnull=False,
    expiry_date__lte=date.today() + timedelta(days=30)
)

    return render(request, "main/dashboard.html", {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_categories": total_categories,
        "low_stock": low_stock,
        "total_stock": total_stock,
        "recent_products": recent_products,
        'labels': labels,
        'data': data,
        'expiring soon':expiring_soon
    })
    

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            return redirect("main:dashboard_view")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "main/login.html")


def logout_view(request):
    logout(request)
    return redirect("main:login")