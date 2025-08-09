from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from inventory.models import Product, Supplier, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum,Count
import json
from datetime import date, timedelta
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.

def landing_view(request):
    return render(request, "main/landing.html")

@login_required
def dashboard_view(request):
    # send_inventory_alert_email()
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
        'expiring_soon': expiring_soon,
        'labels': labels,
        'data': data,
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




def send_inventory_alert_email():
    low_stock = Product.objects.filter(stock_quantity__lt=10)
    expiring_soon = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lte=date.today() + timedelta(days=30)
    )

    alert_dict = {}

    for product in low_stock:
        alert_dict[product.id] = {'product': product, 'reasons': ['Low Stock']}

    for product in expiring_soon:
        if product.id in alert_dict:
            alert_dict[product.id]['reasons'].append('Expiring Soon')
        else:
            alert_dict[product.id] = {'product': product, 'reasons': ['Expiring Soon']}

    alert_items = list(alert_dict.values())

    if alert_items:
        context = {
            'items': alert_items,
            'message': "Some inventory items need your attention."
        }
        html_message = render_to_string("main/mail/alert.html", context)

        email = EmailMessage(
            subject="⚠️ Inventory Alert",
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER], 
        )
        email.content_subtype = "html"
        email.send()
        return True

    return False


#for my notification icon in the navbar
@login_required
def alerts_view(request):
    low_stock = Product.objects.filter(stock_quantity__lt=10)
    expiring_soon = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lte=date.today() + timedelta(days=30)
    )
    alert_dict = {}

    for product in low_stock:
        alert_dict[product.id] = {'product': product, 'reasons': ['Low Stock']}

    for product in expiring_soon:
        if product.id in alert_dict:
            alert_dict[product.id]['reasons'].append('Expiring Soon')
        else:
            alert_dict[product.id] = {'product': product, 'reasons': ['Expiring Soon']}

    alert_items = list(alert_dict.values())
    

    if request.method == "POST":
        sent = send_inventory_alert_email()  
        if sent:
            messages.success(request, "Inventory alert email sent to admin.")
        else:
            messages.info(request, "No alerts to email right now.")
        return redirect("main:alerts_view")  

 
    return render(request, 'main/alerts.html', {
        'items': alert_items,
    })
