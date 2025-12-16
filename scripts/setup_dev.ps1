# Setup development environment (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe scripts\create_superuser.py
Write-Host "Setup complete. Run '.\\.venv\\Scripts\\Activate.ps1' then 'python manage.py runserver'"
