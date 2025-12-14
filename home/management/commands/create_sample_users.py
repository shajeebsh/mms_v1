from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from home.models import UserProfile


class Command(BaseCommand):
    help = 'Create sample users with different user types for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample users...')

        # Sample user data
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@mosque.org',
                'first_name': 'System',
                'last_name': 'Administrator',
                'user_type': 'admin',
                'department': 'IT',
                'phone': '+1-555-0001',
            },
            {
                'username': 'executive1',
                'email': 'chairman@mosque.org',
                'first_name': 'Ahmed',
                'last_name': 'Al-Rashid',
                'user_type': 'executive',
                'department': 'Board of Directors',
                'phone': '+1-555-0002',
            },
            {
                'username': 'executive2',
                'email': 'vice@mosque.org',
                'first_name': 'Fatima',
                'last_name': 'Al-Zahra',
                'user_type': 'executive',
                'department': 'Board of Directors',
                'phone': '+1-555-0003',
            },
            {
                'username': 'manager1',
                'email': 'education@mosque.org',
                'first_name': 'Omar',
                'last_name': 'Al-Hassan',
                'user_type': 'manager',
                'department': 'Education',
                'phone': '+1-555-0004',
            },
            {
                'username': 'manager2',
                'email': 'finance@mosque.org',
                'first_name': 'Aisha',
                'last_name': 'Al-Khalid',
                'user_type': 'manager',
                'department': 'Finance',
                'phone': '+1-555-0005',
            },
            {
                'username': 'staff1',
                'email': 'reception@mosque.org',
                'first_name': 'Mohammed',
                'last_name': 'Al-Sayed',
                'user_type': 'staff',
                'department': 'Operations',
                'phone': '+1-555-0006',
            },
            {
                'username': 'staff2',
                'email': 'maintenance@mosque.org',
                'first_name': 'Zara',
                'last_name': 'Al-Fayed',
                'user_type': 'staff',
                'department': 'Maintenance',
                'phone': '+1-555-0007',
            },
            {
                'username': 'volunteer1',
                'email': 'volunteer1@mosque.org',
                'first_name': 'Ibrahim',
                'last_name': 'Al-Mansoori',
                'user_type': 'volunteer',
                'department': 'Community Service',
                'phone': '+1-555-0008',
            },
        ]

        created_count = 0
        original_users_data = users_data.copy()  # Keep original data for display
        for user_data in users_data:
            # Make a copy to avoid modifying the original
            user_data_copy = user_data.copy()
            
            # Extract user profile data
            user_type = user_data_copy.pop('user_type')
            department = user_data_copy.pop('department')
            phone = user_data_copy.pop('phone')

            # Create or update user
            user, created = User.objects.get_or_create(
                username=user_data_copy['username'],
                defaults=user_data_copy
            )

            if created:
                # Set default password
                user.set_password('password123')
                user.save()

            # Create or update user profile
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': user_type,
                    'department': department,
                    'phone': phone,
                }
            )

            if created or profile_created:
                created_count += 1
                self.stdout.write(f"Created user: {user.username} ({user_type})")
            else:
                self.stdout.write(f"User already exists: {user.username} ({user_type})")

        self.stdout.write(self.style.SUCCESS(f'Successfully processed {created_count} new users'))

        # Display login information
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SAMPLE USER LOGIN CREDENTIALS')
        self.stdout.write('='*50)
        self.stdout.write('All users have password: password123')
        self.stdout.write('')
        for user_data in original_users_data:
            user_type = user_data.get('user_type')
            username = user_data.get('username')
            self.stdout.write(f'{username:12} ({user_type:10}) - {user_data.get("email")}')
        self.stdout.write('')
        self.stdout.write('Access the dashboard at: http://127.0.0.1:8000/dashboard/')
        self.stdout.write('Login page at: http://127.0.0.1:8000/login/')        self.stdout.write('Login page at: http://127.0.0.1:8000/login/')