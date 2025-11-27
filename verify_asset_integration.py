#!/usr/bin/env python
"""
Verification script for Asset App SSO Integration
Checks that all components are properly connected
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.conf import settings
from django.apps import apps
from accounts.models import User
from assets.models import Asset, AssetCategory
from django.contrib.auth import authenticate

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_check(status, message):
    symbol = "✓" if status else "✗"
    print(f"  {symbol} {message}")

def verify_asset_integration():
    """Verify Asset App SSO Integration"""
    print("\n" + "🔍 ASSET APP SSO INTEGRATION VERIFICATION" + "\n")
    
    # Check 1: App Installation
    print_header("1. Application Configuration")
    installed_apps = settings.INSTALLED_APPS
    
    print_check('accounts' in installed_apps, "Accounts app installed")
    print_check('assets' in installed_apps, "Assets app installed")
    print_check('locations' in installed_apps, "Locations app installed")
    print_check('movements' in installed_apps, "Movements app installed")
    
    # Check 2: Authentication Backend
    print_header("2. Authentication Backend")
    auth_backends = settings.AUTHENTICATION_BACKENDS
    
    has_sso_backend = any('BusinessPlatformAuthBackend' in backend for backend in auth_backends)
    has_model_backend = any('ModelBackend' in backend for backend in auth_backends)
    
    print_check(has_sso_backend, "Business Platform SSO backend configured")
    print_check(has_model_backend, "Local authentication fallback enabled")
    
    # Check 3: SSO Configuration
    print_header("3. SSO Configuration")
    
    bp_url = getattr(settings, 'BUSINESS_PLATFORM_URL', None)
    bp_api_key = getattr(settings, 'BUSINESS_PLATFORM_API_KEY', None)
    
    print_check(bool(bp_url), f"Business Platform URL: {bp_url or 'Not configured'}")
    print_check(bool(bp_api_key), f"API Key: {'Configured' if bp_api_key else 'Not configured'}")
    
    # Check 4: Database Models
    print_header("4. Database Models")
    
    try:
        user_model = apps.get_model('accounts', 'User')
        asset_model = apps.get_model('assets', 'Asset')
        category_model = apps.get_model('assets', 'AssetCategory')
        
        print_check(True, f"User model: {user_model.__name__}")
        print_check(True, f"Asset model: {asset_model.__name__}")
        print_check(True, f"Category model: {category_model.__name__}")
        
        # Check foreign key relationships
        asset_fields = {f.name: f for f in asset_model._meta.get_fields()}
        
        has_responsible = 'responsible_person' in asset_fields
        has_created_by = 'created_by' in asset_fields
        
        print_check(has_responsible, "Asset → User relationship (responsible_person)")
        print_check(has_created_by, "Asset → User relationship (created_by)")
        
    except Exception as e:
        print_check(False, f"Error loading models: {str(e)}")
    
    # Check 5: Database Data
    print_header("5. Database Statistics")
    
    try:
        user_count = User.objects.count()
        asset_count = Asset.objects.count()
        category_count = AssetCategory.objects.count()
        
        print(f"  • Users in database: {user_count}")
        print(f"  • Assets in database: {asset_count}")
        print(f"  • Asset categories: {category_count}")
        
        if user_count > 0:
            admin_count = User.objects.filter(role='admin').count()
            manager_count = User.objects.filter(role='location_manager').count()
            personnel_count = User.objects.filter(role='personnel').count()
            
            print(f"\n  Role Distribution:")
            print(f"    - Admins: {admin_count}")
            print(f"    - Location Managers: {manager_count}")
            print(f"    - Personnel: {personnel_count}")
        
        if asset_count > 0:
            assigned_assets = Asset.objects.filter(responsible_person__isnull=False).count()
            print(f"\n  • Assets assigned to users: {assigned_assets}/{asset_count}")
            
    except Exception as e:
        print_check(False, f"Error querying database: {str(e)}")
    
    # Check 6: URL Configuration
    print_header("6. URL Configuration")
    
    from django.urls import resolve, reverse
    
    try:
        # Test key URLs
        urls_to_test = [
            ('accounts:login', 'Login URL'),
            ('assets:list', 'Asset list URL'),
            ('dashboard:index', 'Dashboard URL'),
        ]
        
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                print_check(True, f"{description}: {url}")
            except Exception:
                print_check(False, f"{description}: Not found")
                
    except Exception as e:
        print_check(False, f"Error checking URLs: {str(e)}")
    
    # Check 7: Permissions
    print_header("7. View Protection")
    
    from assets import views
    from django.contrib.auth.mixins import LoginRequiredMixin
    
    view_classes = [
        ('AssetListView', views.AssetListView),
        ('AssetDetailView', views.AssetDetailView),
        ('AssetCreateView', views.AssetCreateView),
        ('AssetUpdateView', views.AssetUpdateView),
    ]
    
    for view_name, view_class in view_classes:
        is_protected = issubclass(view_class, LoginRequiredMixin)
        print_check(is_protected, f"{view_name} requires authentication")
    
    # Summary
    print_header("INTEGRATION STATUS")
    
    all_good = (
        'assets' in installed_apps and
        has_sso_backend and
        bool(bp_url)
    )
    
    if all_good:
        print("\n  ✅ Asset App SSO Integration is ACTIVE and CONFIGURED\n")
        print("  Next Steps:")
        print("  1. Configure Business Platform credentials in .env")
        print("  2. Run: python manage.py sync_users")
        print("  3. Start server: python manage.py runserver")
        print("  4. Login at http://localhost:8000/accounts/login/")
        print("  5. Access assets at http://localhost:8000/assets/")
    else:
        print("\n  ⚠️  Integration has issues - see details above\n")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == '__main__':
    try:
        verify_asset_integration()
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
