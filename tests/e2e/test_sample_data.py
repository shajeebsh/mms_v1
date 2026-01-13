import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_sample_data_navigation(page: Page, live_server_url):
    # 1. Login
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))
    
    # 2. Navigate to Sample Data Management
    page.get_by_role("link", name=re.compile("Sample Data Management")).click()
    
    # Verify page loaded
    expect(page.locator("h1")).to_contain_text("Sample Data Management")
