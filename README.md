# Mosque Management System (MMS)

A comprehensive management system for mosques, built with Django and Wagtail.

## Features
- **Membership Management**: Track families, members, and vital records (Nikah, Janazah, etc.).
- **Finance**: Manage donations, expenses, and membership dues.
- **Education**: Manage classes, teachers, and student enrollments.
- **Operations**: Prayer times, auditorium bookings, and digital signage.
- **Home/Dashboard**: Executive dashboard with key metrics.

## User Roles
The system categorizes users into several roles across different modules:

### System User Types
Primary roles for dashboard and module management:
- **Administrator**: Full system access.
- **Executive Board Member**: High-level oversight and reporting.
- **Department Manager**: Specific module management (Finance, HR, etc.).
- **Staff Member**: Standard operational access.
- **Volunteer**: Restricted access for specific tasks.

### Staff Positions (HR)
Specific roles for mosque employees:
- **Imam / Assistant Imam**
- **Muazzin**
- **Teacher**
- **Administrator**
- **Maintenance / Cleaner**
- **Security Guard**

### Trustee & Committee Roles
Leadership and governance roles:
- **Trustees**: President, Vice President, Secretary, Treasurer.
- **Committee**: Chairperson, Secretary, Minute Taker.

## Setup Instructions

Follow these steps to set up the project on a new machine.

### Prerequisites
- **Python 3.10+**
- **Git**

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mms_v1
```

### 2. Set Up Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
The project uses `django-environ` for configuration. Create a `.env` file in the project root:

```bash
cp .env.example .env  # Or create it manually
```

Update your [`.env`](file:///Users/shajeebs/PythonProjects/mms_v1/.env) with your local database credentials.

### 5. Setup Database
The system uses PostgreSQL for both local development and production. It supports switching between multiple database environments (e.g., `local-dev`, `remote-dev1`).

**1. Configure Database Credentials:**
Update `DATABASE_URL` in `.env` for your local database:
```bash
DATABASE_URL=postgres://postgres:Password1!@127.0.0.1:5432/mms_v1
```

**2. Switching Environments:**
The application defaults to `local-dev`. To switch to a different database (e.g., `remote-dev1`), set the `SELECTED_DATABASE` environment variable in your `.env` file or shell:

```bash
# In .env file
SELECTED_DATABASE=remote-dev1
```

**3. Apply Migrations:**
Ensure you apply migrations to the selected database:
```bash
# Example: Apply migrations to the currently selected database (from .env)
python manage.py migrate

# Example: One-off command for a specific database
SELECTED_DATABASE=remote-dev1 python manage.py migrate
```

**4. MySQL Configuration (Optional):**
To use MySQL instead of PostgreSQL:

1. Install MySQL server and create a database:
   ```sql
   CREATE DATABASE mms_v1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Add `MYSQL_DB_URL` to your `.env` file:
   ```bash
   MYSQL_DB_URL=mysql://username:password@localhost:3306/mms_v1
   ```

3. Switch to MySQL by setting:
   ```bash
   SELECTED_DATABASE=mysql-dev
   ```

4. Install the MySQL client library:
   ```bash
   pip install mysqlclient
   ```

**Seed Sample Data:**
```bash
python manage.py populate_sample_data
```

### 6. Create Admin User
```bash
# Superuser credentials are pre-configured if using sample data:
# Username: admin / Password: adminpassword
python manage.py createsuperuser  # To create a new one
```

### 7. Run the Server
```bash
python manage.py runserver
```

## Deployment & Production
For detailed instructions on deploying to **Google Cloud Run** and **Cloud SQL**, refer to the [walkthrough.md](file:///Users/shajeebs/.gemini/antigravity/brain/e3b9ea35-d83b-484f-9530-3b975abbc9f7/walkthrough.md).

### PythonAnywhere (quick deploy)
```bash
# 1) Pull latest code
git pull

# 2) Activate venv
source ~/.virtualenvs/<your-venv-name>/bin/activate
eg:- source /home/shajeebsh/.virtualenvs/.env/bin/activate

# 3) Install deps (if changed)
pip install -r requirements.txt

# 4) Apply DB migrations
python manage.py migrate

# 5) Static files
python manage.py collectstatic --noinput
```

Then go to the **Web** tab in PythonAnywhere and click **Reload**.

## Accessing the Application
- **Website**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Admin Panel**: [http://127.0.0.1:8000/cms/](http://127.0.0.1:8000/cms/)

## Running Tests

The project includes comprehensive test suites for models, views, and business logic. Here's how to run them:

### Run All Tests
```bash
python manage.py test
```

### Run Tests for a Specific App
```bash
# Run all membership tests
python manage.py test membership

# Run all finance tests
python manage.py test finance
```

### Run Specific Test Files
```bash
# Run model tests
python manage.py test membership.tests

# Run view integration tests
python manage.py test membership.test_views

# Run business logic tests
python manage.py test membership.test_business_logic
```

### Run Specific Test Classes or Methods
```bash
# Run a specific test class
python manage.py test membership.tests.FamilyModelTest

# Run a specific test method
python manage.py test membership.tests.FamilyModelTest.test_family_creation
```

### Test Options

**Verbose Output** (recommended for seeing test details):
```bash
python manage.py test membership --verbosity=2
```

**Keep Test Database** (faster for repeated test runs):
```bash
python manage.py test membership --keepdb
```

**Run Tests in Parallel** (faster execution):
```bash
python manage.py test membership --parallel
```

**Run Tests with Coverage** (if coverage.py is installed):
```bash
coverage run --source='.' manage.py test membership
coverage report
coverage html  # Generates HTML report in htmlcov/
```

### Test Structure

The test suite includes:
- **Unit Tests** (`membership/tests.py`, `finance/tests.py`): Test individual model functionality, validations, and properties
- **Integration Tests** (`membership/test_views.py`): Test view functionality, HTTP requests, and user interactions
- **Business Logic Tests** (`membership/test_business_logic.py`): Test critical business logic like payment processing and dues calculations
- **Automated E2E Tests** (`tests/e2e/`): Browser-based testing using Playwright and Pytest

### Running Automated E2E Tests (Playwright)

The system includes automated browser tests for end-to-end verification covering CRUD operations for all major modules:
- Membership (Families, Members)
- Finance (Donations, Expenses)
- Accounting (Chart of Accounts, Ledger)
- Billing (Invoices, Payments)
- Education (Teachers, Classes)
- Assets (Shops, Property Units)
- Operations (Bookings, Prayer Times)
- HR (Staff, Positions)
- Committee (Committees, Trustees)
- Sample Data

1. **Install Test Dependencies**:
   ```bash
   pip install pytest-playwright
   playwright install chromium
   ```

2. **Run E2E Tests**:
   Ensure the development server is running in another terminal (`python manage.py runserver`), then run the full suite:
   ```bash
   pytest tests/e2e/
   ```

   Or run specific module tests:
   ```bash
   pytest tests/e2e/test_membership.py
   pytest tests/e2e/test_finance.py
   # ...and so on for other modules
   ```

### 3. Generate Test Report
To generate a comprehensive HTML report of the test results:
```bash
pytest tests/e2e/ --html=report.html
```
This will create a `report.html` file in the project directory which you can open in your browser.

## Configuration
- **Membership Dues**: Go to **Settings > System settings** in the admin panel to configure the default monthly dues amount.
