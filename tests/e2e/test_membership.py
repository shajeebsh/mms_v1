import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_membership_crud(page: Page, live_server_url):
    # 1. Login
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Navigate to Membership -> Members
    page.get_by_role("button", name=re.compile("Membership")).click()
    page.get_by_role("link", name=re.compile("Members")).first.click()
    
    # Verify we are on Members page
    expect(page.locator("h1")).to_contain_text("Members")
    
    # 3. Navigate to House Registrations
    page.get_by_role("link", name=re.compile("House Registrations")).click()
    expect(page.locator("h1")).to_contain_text("House Registrations")

    # 4. Navigate to Membership Dues
    page.get_by_role("link", name=re.compile("Membership Dues")).click()
    expect(page.locator("h1")).to_contain_text("Membership Dues")
