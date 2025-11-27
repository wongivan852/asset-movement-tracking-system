from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from assets.models import Asset, AssetCategory
from movements.models import Movement, BulkMovement, StockTake, MovementAcknowledgement
from locations.models import Location


class Command(BaseCommand):
    help = 'Set up user groups with specific permissions for Asset Movement Tracking'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user groups and permissions...\n')

        # Group 0: Viewers - View only, no actions allowed
        group0, created = Group.objects.get_or_create(name='Viewers')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created group: {group0.name}'))
        else:
            self.stdout.write(f'Group already exists: {group0.name}')
            group0.permissions.clear()

        # Group 1: Asset Operators - Can view assets and create movements (status: pending)
        group1, created = Group.objects.get_or_create(name='Asset Operators')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created group: {group1.name}'))
        else:
            self.stdout.write(f'Group already exists: {group1.name}')
            group1.permissions.clear()

        # Group 2: Movement Approvers - Can accept pending and change to completed/delivered
        group2, created = Group.objects.get_or_create(name='Movement Approvers')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created group: {group2.name}'))
        else:
            self.stdout.write(f'Group already exists: {group2.name}')
            group2.permissions.clear()

        # Group 3: Asset Administrators - Full access to all operations
        group3, created = Group.objects.get_or_create(name='Asset Administrators')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created group: {group3.name}'))
        else:
            self.stdout.write(f'Group already exists: {group3.name}')
            group3.permissions.clear()

        # Get content types
        asset_ct = ContentType.objects.get_for_model(Asset)
        asset_category_ct = ContentType.objects.get_for_model(AssetCategory)
        movement_ct = ContentType.objects.get_for_model(Movement)
        bulk_movement_ct = ContentType.objects.get_for_model(BulkMovement)
        stock_take_ct = ContentType.objects.get_for_model(StockTake)
        acknowledgement_ct = ContentType.objects.get_for_model(MovementAcknowledgement)
        location_ct = ContentType.objects.get_for_model(Location)

        # ===========================================
        # Group 0: Viewers Permissions
        # - View only, no actions allowed
        # ===========================================
        group0_permissions = []

        # View-only permissions for assets
        group0_permissions.append(Permission.objects.get(codename='view_asset', content_type=asset_ct))
        group0_permissions.append(Permission.objects.get(codename='view_assetcategory', content_type=asset_category_ct))

        # View-only permissions for locations
        group0_permissions.append(Permission.objects.get(codename='view_location', content_type=location_ct))

        # View-only permissions for movements
        group0_permissions.append(Permission.objects.get(codename='view_movement', content_type=movement_ct))
        group0_permissions.append(Permission.objects.get(codename='view_bulkmovement', content_type=bulk_movement_ct))

        group0.permissions.set(group0_permissions)
        self.stdout.write(f'  - Assigned {len(group0_permissions)} permissions to {group0.name}')

        # ===========================================
        # Group 1: Asset Operators Permissions
        # - View assets and locations
        # - Create movements (status will be pending)
        # ===========================================
        group1_permissions = []

        # Asset permissions - view only
        group1_permissions.append(Permission.objects.get(codename='view_asset', content_type=asset_ct))
        group1_permissions.append(Permission.objects.get(codename='view_assetcategory', content_type=asset_category_ct))

        # Location permissions - view only
        group1_permissions.append(Permission.objects.get(codename='view_location', content_type=location_ct))

        # Movement permissions - view and add (create pending movements)
        group1_permissions.append(Permission.objects.get(codename='view_movement', content_type=movement_ct))
        group1_permissions.append(Permission.objects.get(codename='add_movement', content_type=movement_ct))

        # Bulk Movement permissions - view and add
        group1_permissions.append(Permission.objects.get(codename='view_bulkmovement', content_type=bulk_movement_ct))
        group1_permissions.append(Permission.objects.get(codename='add_bulkmovement', content_type=bulk_movement_ct))

        group1.permissions.set(group1_permissions)
        self.stdout.write(f'  - Assigned {len(group1_permissions)} permissions to {group1.name}')

        # ===========================================
        # Group 2: Movement Approvers Permissions
        # - All Group 1 permissions
        # - Change movement status (pending -> completed/delivered)
        # - Add acknowledgements
        # ===========================================
        group2_permissions = list(group1_permissions)  # Include all Group 1 permissions

        # Movement permissions - add change permission
        group2_permissions.append(Permission.objects.get(codename='change_movement', content_type=movement_ct))

        # Bulk Movement permissions - add change permission
        group2_permissions.append(Permission.objects.get(codename='change_bulkmovement', content_type=bulk_movement_ct))

        # Acknowledgement permissions
        group2_permissions.append(Permission.objects.get(codename='view_movementacknowledgement', content_type=acknowledgement_ct))
        group2_permissions.append(Permission.objects.get(codename='add_movementacknowledgement', content_type=acknowledgement_ct))
        group2_permissions.append(Permission.objects.get(codename='change_movementacknowledgement', content_type=acknowledgement_ct))

        group2.permissions.set(group2_permissions)
        self.stdout.write(f'  - Assigned {len(group2_permissions)} permissions to {group2.name}')

        # ===========================================
        # Group 3: Asset Administrators Permissions
        # - Full access to all models
        # ===========================================
        group3_permissions = []

        # Full Asset permissions
        for perm in Permission.objects.filter(content_type=asset_ct):
            group3_permissions.append(perm)
        for perm in Permission.objects.filter(content_type=asset_category_ct):
            group3_permissions.append(perm)

        # Full Location permissions
        for perm in Permission.objects.filter(content_type=location_ct):
            group3_permissions.append(perm)

        # Full Movement permissions
        for perm in Permission.objects.filter(content_type=movement_ct):
            group3_permissions.append(perm)
        for perm in Permission.objects.filter(content_type=bulk_movement_ct):
            group3_permissions.append(perm)

        # Full Acknowledgement permissions
        for perm in Permission.objects.filter(content_type=acknowledgement_ct):
            group3_permissions.append(perm)

        # Full Stock Take permissions
        for perm in Permission.objects.filter(content_type=stock_take_ct):
            group3_permissions.append(perm)

        group3.permissions.set(group3_permissions)
        self.stdout.write(f'  - Assigned {len(group3_permissions)} permissions to {group3.name}')

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('User groups setup completed successfully!'))
        self.stdout.write('=' * 60)
        self.stdout.write('\nGroup Summary:')
        self.stdout.write('-' * 60)

        self.stdout.write(self.style.WARNING('\n0. Viewers (No Authority):'))
        self.stdout.write('   - Can VIEW assets, locations, and movements')
        self.stdout.write('   - CANNOT create, edit, or delete anything')
        self.stdout.write('   - Read-only access')

        self.stdout.write(self.style.WARNING('\n1. Asset Operators:'))
        self.stdout.write('   - Can VIEW assets and locations')
        self.stdout.write('   - Can CREATE movements (status: pending)')
        self.stdout.write('   - Cannot approve or complete movements')

        self.stdout.write(self.style.WARNING('\n2. Movement Approvers:'))
        self.stdout.write('   - All Asset Operators permissions PLUS:')
        self.stdout.write('   - Can APPROVE pending movements')
        self.stdout.write('   - Can change status to: Completed (internal) or Delivered (client)')
        self.stdout.write('   - Can add acknowledgements')

        self.stdout.write(self.style.WARNING('\n3. Asset Administrators:'))
        self.stdout.write('   - FULL ACCESS to all operations')
        self.stdout.write('   - Can manage assets, locations, movements, stock takes')
        self.stdout.write('   - Can delete records')

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('To assign users to groups, go to Django Admin > Users')
        self.stdout.write('or use: user.groups.add(Group.objects.get(name="Group Name"))')
        self.stdout.write('=' * 60 + '\n')
