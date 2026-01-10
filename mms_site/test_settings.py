from .settings import *

# Force SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable tasks for tests
DJANGO_TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.dummy.DummyBackend",
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
