from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category,Supplier
from .forms import ProductForm
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date, timedelta
from django.db.models import Count
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def product_list(request):
    query = request.GET.get("q")
    products = Product.objects.all()
    recent_products = Product.objects.order_by("-id")[:4]
    expiring_soon_list = Product.objects.filter(expiry_date__lte=date.today() + timedelta(days=30))
    low_stock = Product.objects.filter(stock_quantity__lte=10)

    filter_type = request.GET.get("filter")

    if filter_type == "low":
        products = Product.objects.filter(stock_quantity__lte=10)
    elif filter_type == "expiring":
        products = Product.objects.filter(expiry_date__lte=date.today() + timedelta(days=30))
    elif query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(suppliers__name__icontains=query)
        ).distinct()

    paginator = Paginator(products, 4)
    page = request.GET.get("page")
    products_page = paginator.get_page(page)

    context = {
        "products": products_page,
        "recent_products": recent_products,
        "low_stock": low_stock.count(),
        "expiring_soon": expiring_soon_list.count(),
        "total_products": Product.objects.count(),
        "total_categories": Category.objects.count(),
        "total_suppliers": Supplier.objects.count(),
    }

    return render(request, "inventory/product_list.html", context)

    
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "inventory/product_detail.html", {"product": product})

from django.contrib import messages

def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect("inventory:product_list")
    else:
        form = ProductForm()

    return render(request, "inventory/product_form.html", {"form": form})


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully!")
        return redirect("inventory:product_list")
    return render(request, "inventory/product_form.html", {"form": form, "title": "Edit Product"})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect("inventory:product_list")
    return render(request, "inventory/product_confirm_delete.html", {"product": product})

