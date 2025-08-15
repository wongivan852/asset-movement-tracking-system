from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from locations.models import Location
from assets.models import AssetCategory, Asset
from movements.models import Movement
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with initial sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create users
        self.create_users()
        
        # Create locations
        self.create_locations()
        
        # Create asset categories
        self.create_categories()
        
        # Create assets
        self.create_assets()
        
        # Create movements
        self.create_movements()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Admin user (already exists)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('password')
            admin_user.save()
        
        # Manager user
        manager_user, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@example.com',
                'first_name': 'Location',
                'last_name': 'Manager',
                'role': 'location_manager',
                'department': 'Operations'
            }
        )
        if created:
            manager_user.set_password('password')
            manager_user.save()
        
        # Staff user
        staff_user, created = User.objects.get_or_create(
            username='staff',
            defaults={
                'email': 'staff@example.com',
                'first_name': 'Staff',
                'last_name': 'Member',
                'role': 'personnel',
                'department': 'Logistics'
            }
        )
        if created:
            staff_user.set_password('password')
            staff_user.save()

    def create_locations(self):
        self.stdout.write('Creating locations...')
        
        manager = User.objects.get(username='manager')
        
        Location.objects.get_or_create(
            code='HK',
            defaults={
                'name': 'Hong Kong Office',
                'address': '123 Central District, Hong Kong',
                'city': 'Hong Kong',
                'country': 'Hong Kong SAR',
                'contact_email': 'hk@company.com',
                'contact_phone': '+852 1234 5678',
                'responsible_person': manager
            }
        )
        
        Location.objects.get_or_create(
            code='SZ',
            defaults={
                'name': 'Shenzhen Office',
                'address': '456 Futian District, Shenzhen',
                'city': 'Shenzhen',
                'country': 'China',
                'contact_email': 'sz@company.com',
                'contact_phone': '+86 755 8765 4321',
                'responsible_person': manager
            }
        )

    def create_categories(self):
        self.stdout.write('Creating asset categories...')
        
        categories = [
            {'name': 'IT Equipment', 'description': 'Computers, servers, networking equipment'},
            {'name': 'Office Furniture', 'description': 'Desks, chairs, cabinets'},
            {'name': 'Electronics', 'description': 'Monitors, printers, phones'},
            {'name': 'Tools & Equipment', 'description': 'Various tools and equipment'},
            {'name': 'Vehicles', 'description': 'Company vehicles'}
        ]
        
        for cat_data in categories:
            AssetCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )

    def create_assets(self):
        self.stdout.write('Creating assets...')
        
        hk_location = Location.objects.get(code='HK')
        sz_location = Location.objects.get(code='SZ')
        admin_user = User.objects.get(username='admin')
        
        it_category = AssetCategory.objects.get(name='IT Equipment')
        furniture_category = AssetCategory.objects.get(name='Office Furniture')
        
        assets_data = [
            {
                'asset_id': 'LAP001',
                'name': 'Dell Latitude 7420',
                'description': 'Dell business laptop with Intel i7 processor',
                'category': it_category,
                'serial_number': 'DL74201234',
                'manufacturer': 'Dell',
                'purchase_value': 1200.00,
                'current_value': 800.00,
                'current_location': hk_location
            },
            {
                'asset_id': 'LAP002',
                'name': 'MacBook Pro 13"',
                'description': 'Apple MacBook Pro with M1 chip',
                'category': it_category,
                'serial_number': 'MBP13M1001',
                'manufacturer': 'Apple',
                'purchase_value': 1600.00,
                'current_value': 1200.00,
                'current_location': hk_location
            },
            {
                'asset_id': 'DSK001',
                'name': 'Adjustable Standing Desk',
                'description': 'Electric height adjustable desk',
                'category': furniture_category,
                'serial_number': 'ASD001',
                'manufacturer': 'Herman Miller',
                'purchase_value': 800.00,
                'current_value': 600.00,
                'current_location': sz_location
            },
            {
                'asset_id': 'CHR001',
                'name': 'Ergonomic Office Chair',
                'description': 'Ergonomic office chair with lumbar support',
                'category': furniture_category,
                'serial_number': 'EOC001',
                'manufacturer': 'Steelcase',
                'purchase_value': 600.00,
                'current_value': 400.00,
                'current_location': sz_location
            },
        ]
        
        for asset_data in assets_data:
            Asset.objects.get_or_create(
                asset_id=asset_data['asset_id'],
                defaults={
                    **asset_data,
                    'created_by': admin_user,
                    'purchase_date': timezone.now().date() - timedelta(days=365)
                }
            )

    def create_movements(self):
        self.stdout.write('Creating sample movements...')
        
        hk_location = Location.objects.get(code='HK')
        sz_location = Location.objects.get(code='SZ')
        admin_user = User.objects.get(username='admin')
        
        # Get some assets to move
        laptop = Asset.objects.get(asset_id='LAP001')
        
        # Create a completed movement
        Movement.objects.get_or_create(
            asset=laptop,
            from_location=hk_location,
            to_location=sz_location,
            defaults={
                'initiated_by': admin_user,
                'status': 'acknowledged',
                'reason': 'Employee relocation',
                'expected_arrival_date': timezone.now() - timedelta(days=2),
                'actual_departure_date': timezone.now() - timedelta(days=3),
                'actual_arrival_date': timezone.now() - timedelta(days=1),
                'notes': 'Laptop transferred for relocated employee'
            }
        )
        
        # Create a pending movement
        chair = Asset.objects.get(asset_id='CHR001')
        Movement.objects.get_or_create(
            asset=chair,
            from_location=sz_location,
            to_location=hk_location,
            defaults={
                'initiated_by': admin_user,
                'status': 'pending',
                'reason': 'Office setup',
                'expected_arrival_date': timezone.now() + timedelta(days=2),
                'notes': 'Chair needed for new office setup'
            }
        )
