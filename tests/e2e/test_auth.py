import pytest

def test_login_page_loads(page):
    # This assumes the app is running on localhost:8000
    page.goto("http://localhost:8000/cms/login/")
    assert "Sign in" in page.title()
    assert page.locator('input[name="username"]').is_visible()
    assert page.locator('input[name="password"]').is_visible()

def test_successful_admin_login(page):
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Verify navigation to dashboard
    assert "Dashboard" in page.title() or page.locator('text=Welcome to the MMS').is_visible()
