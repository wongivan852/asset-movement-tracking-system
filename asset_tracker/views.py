from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    """Home page view - redirects to dashboard if logged in"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'home.html')


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    user = request.user
    
    if user.role == 'admin':
        return redirect('dashboard:admin')
    elif user.role == 'location_manager':
        return redirect('dashboard:manager')
    else:
        return redirect('dashboard:staff')
