import pytest


@pytest.mark.django_db
def test_login_page_loads(page, live_server_url):
    page.goto(f"{live_server_url}/cms/login/")
    assert "Sign in" in page.title()
    assert page.locator('input[name="username"]').is_visible()
    assert page.locator('input[name="password"]').is_visible()


@pytest.mark.django_db
def test_successful_admin_login(page, live_server_url):
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Verify navigation to dashboard
    assert "Dashboard" in page.title() or page.locator('text=Welcome to the MMS').is_visible()
