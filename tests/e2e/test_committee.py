import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_committee_crud(page: Page, live_server_url):
    # 1. Login
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Navigate to Committee & Minutes
    page.get_by_role("button", name=re.compile("Committee & Minutes")).click()
    page.get_by_role("link", name=re.compile("Committees")).click()
    
    # Verify page loaded
    expect(page.locator("h1")).to_contain_text("Committees")

    # 3. Navigate to Trustees
    page.get_by_role("link", name=re.compile("Trustees")).click()
    expect(page.locator("h1")).to_contain_text("Trustees")
