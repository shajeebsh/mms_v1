import os
import pytest

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(scope="function")
def admin_user(db):
    """Create admin user for E2E tests."""
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@example.com",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    if created:
        user.set_password("adminpassword")
        user.save()
    return user


@pytest.fixture(scope="function")
def live_server_url(live_server, admin_user):
    """Provide live server URL with admin user created."""
    return live_server.url
