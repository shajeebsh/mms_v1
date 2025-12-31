import pytest

def test_module_navigation(page):
    # Login first
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Check for Membership menu
    membership_menu = page.locator('text=🏠 Membership')
    assert membership_menu.is_visible()
    
    # Navigate to Sample Data Management
    # Since it's in the side menu, we might need to click more items or go directly
    page.goto("http://localhost:8000/cms/admin/sample-data-management/")
    assert "Sample Data Management" in page.content()
    assert page.locator('text=Accounting & Ledger').is_visible()
