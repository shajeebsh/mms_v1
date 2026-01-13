import pytest


@pytest.mark.django_db
def test_module_navigation(page, live_server_url):
    # Login first
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Go directly to verify page content
    page.goto(f"{live_server_url}/cms/admin/sample-data-management/")
    # Wait for the heading to appear
    assert page.locator('h1:has-text("Sample Data Management")').is_visible()
    assert page.locator('text=Accounting & Ledger').is_visible()
