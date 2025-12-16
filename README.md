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

## Configuration
- **Membership Dues**: Go to **Settings > System settings** in the admin panel to configure the default monthly dues amount.
