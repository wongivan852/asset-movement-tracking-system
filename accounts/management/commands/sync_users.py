from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.sso import sso_client

User = get_user_model()


class Command(BaseCommand):
    help = 'Synchronize users from Business Platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Sync specific user by username',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        if username:
            # Sync specific user
            self.sync_single_user(username, dry_run)
        else:
            # Sync all users
            self.sync_all_users(dry_run)
    
    def sync_single_user(self, username, dry_run=False):
        """Sync a single user from business platform"""
        self.stdout.write(f'Fetching user: {username}')
        
        user_data = sso_client.get_user_info(username=username)
        
        if not user_data:
            self.stdout.write(self.style.ERROR(f'User {username} not found in business platform'))
            return
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Would sync user: {username}'))
            self.stdout.write(f'  Email: {user_data.get("email")}')
            self.stdout.write(f'  Role: {user_data.get("role")}')
            self.stdout.write(f'  Department: {user_data.get("department")}')
        else:
            result = sso_client.sync_user(user_data)
            if result == 'created':
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            elif result == 'updated':
                self.stdout.write(self.style.SUCCESS(f'Updated user: {username}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to sync user: {username}'))
    
    def sync_all_users(self, dry_run=False):
        """Sync all users from business platform"""
        self.stdout.write('Synchronizing all users from Business Platform...')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - Fetching users...'))
            # In dry run, just show what would happen
            # You would need to implement a dry-run version of sync_all_users
            self.stdout.write(self.style.WARNING('Dry run mode for all users not fully implemented'))
            return
        
        created, updated, errors = sso_client.sync_all_users()
        
        self.stdout.write(self.style.SUCCESS(f'Synchronization complete!'))
        self.stdout.write(f'  Created: {created} users')
        self.stdout.write(f'  Updated: {updated} users')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'  Errors: {len(errors)}'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'    - {error}'))
