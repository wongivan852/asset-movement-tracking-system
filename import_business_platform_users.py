#!/usr/bin/env python
"""
Import users from integrated business platform to asset tracking system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

import json
from accounts.models import User
from django.db import transaction

# Path to business platform user export
BUSINESS_PLATFORM_PATH = '/home/wongivan852/projects/integrated_business_platform'
USER_EXPORT_FILE = f'{BUSINESS_PLATFORM_PATH}/users_export_formatted.json'

def import_users_from_business_platform():
    """Import all users from business platform export"""
    
    print("=" * 70)
    print("  IMPORTING USERS FROM BUSINESS PLATFORM")
    print("=" * 70)
    
    # Read user data
    try:
        with open(USER_EXPORT_FILE, 'r') as f:
            users_data = json.load(f)
    except FileNotFoundError:
        print(f"\n❌ Error: User export file not found at {USER_EXPORT_FILE}")
        print("   Please ensure the integrated business platform is available.")
        return
    except json.JSONDecodeError as e:
        print(f"\n❌ Error: Invalid JSON in user export file: {str(e)}")
        return
    
    print(f"\nFound {len(users_data)} users to import\n")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []
    
    with transaction.atomic():
        for user_data in users_data:
            try:
                username = user_data.get('username')
                email = user_data.get('email')
                
                if not username:
                    skipped_count += 1
                    print(f"⊘ Skipped: No username provided")
                    continue
                
                # Map role based on is_superuser and is_staff
                if user_data.get('is_superuser'):
                    role = 'admin'
                elif user_data.get('is_staff'):
                    role = 'location_manager'
                else:
                    role = 'personnel'
                
                # Get or create user
                user, created = User.objects.update_or_create(
                    username=username,
                    defaults={
                        'email': email or '',
                        'first_name': user_data.get('first_name', ''),
                        'last_name': user_data.get('last_name', ''),
                        'employee_id': user_data.get('employee_id', ''),
                        'department': user_data.get('department', ''),
                        'role': role,
                        'is_active': bool(user_data.get('is_active', 1)),
                        'is_staff': bool(user_data.get('is_staff', 0)),
                        'is_superuser': bool(user_data.get('is_superuser', 0)),
                    }
                )
                
                # Set unusable password for SSO users
                if created:
                    user.set_unusable_password()
                    user.save()
                
                if created:
                    created_count += 1
                    status = "✓ Created"
                else:
                    updated_count += 1
                    status = "↻ Updated"
                
                role_badge = {
                    'admin': '(ADMIN)',
                    'location_manager': '(MANAGER)',
                    'personnel': '(USER)'
                }.get(role, '')
                
                print(f"{status}: {username:40} | {user.get_full_name():25} | {role_badge}")
                
            except Exception as e:
                errors.append(f"{username}: {str(e)}")
                print(f"✗ Error: {username} - {str(e)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("  IMPORT SUMMARY")
    print("=" * 70)
    print(f"\nTotal users processed: {len(users_data)}")
    print(f"  ✓ Created: {created_count}")
    print(f"  ↻ Updated: {updated_count}")
    print(f"  ⊘ Skipped: {skipped_count}")
    print(f"  ✗ Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  • {error}")
    
    # Display current user count
    total_users = User.objects.filter(is_active=True).count()
    admin_count = User.objects.filter(is_active=True, role='admin').count()
    manager_count = User.objects.filter(is_active=True, role='location_manager').count()
    personnel_count = User.objects.filter(is_active=True, role='personnel').count()
    
    print(f"\nCurrent system statistics:")
    print(f"  • Total active users: {total_users}")
    print(f"  • Admins: {admin_count}")
    print(f"  • Location Managers: {manager_count}")
    print(f"  • Personnel: {personnel_count}")
    
    print("\n" + "=" * 70)
    print("✅ User import completed successfully!")
    print("=" * 70)
    print("\nYou can now:")
    print("  1. View users at: http://localhost:8000/accounts/users/")
    print("  2. Users can login with their Business Platform credentials")
    print("  3. Set passwords for local login (optional):")
    print("     python manage.py changepassword <username>")
    print()

if __name__ == '__main__':
    try:
        import_users_from_business_platform()
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
