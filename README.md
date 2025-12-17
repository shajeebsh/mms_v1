# Mosque Management System (MMS)

A comprehensive management system for mosques, built with Django and Wagtail.

## Features
- **Membership Management**: Track families, members, and vital records (Nikah, Janazah, etc.).
- **Finance**: Manage donations, expenses, and membership dues.
- **Education**: Manage classes, teachers, and student enrollments.
- **Operations**: Prayer times, auditorium bookings, and digital signage.
- **Home/Dashboard**: Executive dashboard with key metrics.

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

### 4. Setup Database
Initialize the SQLite database and apply migrations.
```bash
python manage.py migrate
```

### 5. Create Admin User
Create a superuser to access the admin panel.
```bash
python manage.py createsuperuser
```

### 6. Run the Server
```bash
python manage.py runserver
```

## Accessing the Application
- **Website**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Admin Panel**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

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

## Configuration
- **Membership Dues**: Go to **Settings > System settings** in the admin panel to configure the default monthly dues amount.
