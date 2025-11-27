from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from locations.models import Location
from assets.models import AssetCategory, Asset
from movements.models import Movement, StockTake, MovementAcknowledgement

User = get_user_model()


class Command(BaseCommand):
    help = 'Remove all sample data from the database (keeps superusers)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Remove all data including superusers',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                'WARNING: This will delete all data from the database!'
            ))
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        self.stdout.write('Removing sample data...')
        
        # Delete movements and related data
        self.stdout.write('Deleting movement acknowledgements...')
        count = MovementAcknowledgement.objects.all().count()
        MovementAcknowledgement.objects.all().delete()
        self.stdout.write(f'  Deleted {count} acknowledgements')
        
        self.stdout.write('Deleting movements...')
        count = Movement.objects.all().count()
        Movement.objects.all().delete()
        self.stdout.write(f'  Deleted {count} movements')
        
        self.stdout.write('Deleting stock takes...')
        count = StockTake.objects.all().count()
        StockTake.objects.all().delete()
        self.stdout.write(f'  Deleted {count} stock takes')
        
        # Delete assets
        self.stdout.write('Deleting assets...')
        count = Asset.objects.all().count()
        Asset.objects.all().delete()
        self.stdout.write(f'  Deleted {count} assets')
        
        # Delete asset categories
        self.stdout.write('Deleting asset categories...')
        count = AssetCategory.objects.all().count()
        AssetCategory.objects.all().delete()
        self.stdout.write(f'  Deleted {count} categories')
        
        # Delete locations
        self.stdout.write('Deleting locations...')
        count = Location.objects.all().count()
        Location.objects.all().delete()
        self.stdout.write(f'  Deleted {count} locations')
        
        # Delete users (except superusers unless --all flag is used)
        if options['all']:
            self.stdout.write('Deleting all users...')
            count = User.objects.all().count()
            User.objects.all().delete()
            self.stdout.write(f'  Deleted {count} users')
        else:
            self.stdout.write('Deleting non-superuser users...')
            count = User.objects.filter(is_superuser=False).count()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f'  Deleted {count} users (kept superusers)')
        
        self.stdout.write(self.style.SUCCESS('All sample data has been removed!'))
        
        if not options['all']:
            self.stdout.write(self.style.WARNING(
                'Note: Superuser accounts were preserved. Use --all flag to remove them too.'
            ))
