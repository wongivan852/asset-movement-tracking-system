#!/usr/bin/env python3
"""
Import users from Business Platform CSV export to Asset Tracker
Processes the active_users_26.csv file
"""

import csv
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.db import transaction
from accounts.models import User

def import_users_from_csv(csv_path):
    """Import users from CSV file"""
    
    imported_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []
    
    print(f"\n{'='*60}")
    print(f"IMPORTING USERS FROM CSV")
    print(f"{'='*60}\n")
    print(f"CSV File: {csv_path}\n")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            users_data = list(reader)
        
        print(f"Found {len(users_data)} users in CSV file\n")
        
        with transaction.atomic():
            for row in users_data:
                try:
                    # Parse CSV data
                    email = row['email'].strip()
                    username = row['username'].strip()
                    first_name = row['first_name'].strip()
                    last_name = row['last_name'].strip()
                    is_active = row['is_active'].strip().lower() in ('t', 'true', '1')
                    is_staff = row['is_staff'].strip().lower() in ('t', 'true', '1')
                    employee_id = row.get('employee_id', '').strip()
                    region = row.get('region', 'HK').strip()
                    department = row.get('department', '').strip()
                    
                    # Check if user already exists
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': username,
                            'first_name': first_name,
                            'last_name': last_name,
                            'is_active': is_active,
                            'is_staff': is_staff,
                            'employee_id': employee_id,
                            'region': region,
                            'department': department,
                        }
                    )
                    
                    if created:
                        # Set a default password for new users
                        user.set_password('changeme123')
                        user.save()
                        imported_count += 1
                        status = '✅ IMPORTED'
                    else:
                        # Update existing user's information
                        user.username = username
                        user.first_name = first_name
                        user.last_name = last_name
                        user.is_active = is_active
                        user.is_staff = is_staff
                        user.employee_id = employee_id
                        user.region = region
                        user.department = department
                        user.save()
                        updated_count += 1
                        status = '🔄 UPDATED'
                    
                    print(f"{status}: {first_name} {last_name} ({email})")
                    print(f"   - Employee ID: {employee_id}")
                    print(f"   - Region: {region} | Department: {department}")
                    print(f"   - Staff: {is_staff} | Active: {is_active}\n")
                    
                except Exception as e:
                    error_msg = f"Error importing {email}: {str(e)}"
                    errors.append(error_msg)
                    skipped_count += 1
                    print(f"❌ SKIPPED: {email} - {str(e)}\n")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"IMPORT SUMMARY")
        print(f"{'='*60}\n")
        print(f"✅ New users imported:    {imported_count}")
        print(f"🔄 Existing users updated: {updated_count}")
        print(f"❌ Users skipped:          {skipped_count}")
        print(f"📊 Total processed:        {imported_count + updated_count + skipped_count}")
        
        if errors:
            print(f"\n⚠️  ERRORS:")
            for error in errors:
                print(f"   - {error}")
        
        # Final database count
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        print(f"\n{'='*60}")
        print(f"FINAL DATABASE STATUS")
        print(f"{'='*60}\n")
        print(f"Total users in database:   {total_users}")
        print(f"Active users:              {active_users}")
        print(f"Staff users:               {staff_users}")
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Fatal error during import: {str(e)}")
        raise

if __name__ == '__main__':
    # Path to the CSV file in the Business Platform directory
    csv_path = '/home/wongivan852/projects/integrated_business_platform/active_users_26.csv'
    
    print("\n" + "="*60)
    print("ASSET TRACKER - USER IMPORT FROM BUSINESS PLATFORM CSV")
    print("="*60)
    
    import_users_from_csv(csv_path)
    
    print("\n✅ Import process completed!")
