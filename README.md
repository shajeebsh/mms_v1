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

This guide covers setting up an existing Wagtail project on your local machine using Python 3.10+ (the standard for late 2025).
1. Install Python
Before downloading the project, ensure Python is installed and added to your system path.
macOS:
Install Homebrew if not already present.
Run brew install python in your terminal.
Verify by running: python3 --version
Windows:
Download the latest stable installer from Python.org.
Important: Check the box "Add Python to PATH" during installation.
Verify by running: python --version
2. Clone the Project
Download the project files from your version control system (e.g., GitHub, GitLab).
bash
# Clone the repository
git clone <your-repository-url>

# Enter the project directory
cd <project-folder-name>
Use code with caution.

3. Set Up a Virtual Environment
This keeps the project's specific Wagtail and Django versions isolated from your system.
Operating System	Command to Create	Command to Activate
macOS	python3 -m venv venv	source venv/bin/activate
Windows	python -m venv venv	venv\Scripts\activate
4. Install Dependencies
Existing projects include a requirements.txt file that lists all necessary packages (Wagtail, Django, etc.).
bash
pip install -r requirements.txt
Use code with caution.

5. Configure Local Settings & Database
Existing projects often have a local.py or .env file for local secrets. Ensure you check for a sample.env or settings/local.py.example and rename it to local.py if necessary.
Initialize the Database:
bash
# Apply existing database migrations
python manage.py migrate

# Create your own local admin account
python manage.py createsuperuser
Use code with caution.

6. Run the Project
Start the Django development server to view the site locally.
bash
python manage.py runserver
Use code with caution.

Front-end Site: http://127.0.0.1:8000
Wagtail Admin: 127.0.0.1 (Log in with the superuser you just created).
Troubleshooting Tips for 2025
Node.js/NPM: If the project uses custom frontend assets (Tailwind, React, etc.), you may also need to run npm install and npm run build within the theme folder.
PostgreSQL: If the project requires PostgreSQL instead of SQLite, ensure Postgres.app (macOS) or PostgreSQL Installer (Windows) is running before you migrate.



