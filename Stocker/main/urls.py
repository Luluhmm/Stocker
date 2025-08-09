from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = "main"

urlpatterns = [
    path('', views.landing_view, name="landing"),
    path('dashboard/', views.dashboard_view, name="dashboard_view"),
    path("login/", views.login_view, name="login"), 
    path("logout/", views.logout_view, name="logout"),
    path("alerts/", views.alerts_view, name="alerts_view"),
    
]