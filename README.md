# Wagtail scaffold (minimal)

This repository provides a minimal Wagtail site scaffold.

Quick start (macOS / Unix):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin: http://127.0.0.1:8000/admin/
