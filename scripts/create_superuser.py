import os
import sys

# Ensure project root is on path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mms_site.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
email = 'admin@example.com'
password = 'password123'

u = User.objects.filter(username=username).first()
if u:
    u.is_staff = True
    u.is_superuser = True
    u.set_password(password)
    u.email = email
    u.save()
    print('Updated existing superuser `admin` with new password')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Created superuser `admin`')

# Create test groups and users for each user type
from django.contrib.auth.models import Group
from home.models import UserProfile

groups = ["membership", "finance", "education", "assets", "operations", "hr", "committee"]
for g in groups:
    Group.objects.get_or_create(name=g)

test_users = {
    "membership_user": "membership",
    "finance_user": "finance",
    "education_user": "education",
    "assets_user": "assets",
    "operations_user": "operations",
    "hr_user": "hr",
    "committee_user": "committee",
}

for tu, group_name in test_users.items():
    user = User.objects.filter(username=tu).first()
    if user:
        user.is_staff = True
        user.set_password(password)
        user.email = f"{tu}@example.com"
        user.save()
        print(f"Updated test user {tu}")
    else:
        user = User.objects.create_user(username=tu, email=f"{tu}@example.com", password=password)
        user.is_staff = True
        user.save()
        print(f"Created test user {tu}")
    grp = Group.objects.get(name=group_name)
    user.groups.add(grp)
    # create or update user profile mapping group -> user_type
    # simple mapping: groups are department managers
    profile, created = UserProfile.objects.get_or_create(user=user)
    # map group to a user_type: managers for department groups
    profile.user_type = 'manager'
    profile.department = group_name
    profile.save()
