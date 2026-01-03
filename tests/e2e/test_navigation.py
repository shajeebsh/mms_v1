import pytest

def test_module_navigation(page):
    # Login first
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Go directly to verify page content
    page.goto("http://localhost:8000/cms/admin/sample-data-management/")
    # Wait for the heading to appear
    assert page.locator('h1:has-text("Sample Data Management")').is_visible()
    assert page.locator('text=Accounting & Ledger').is_visible()
