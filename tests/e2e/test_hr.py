import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_hr_crud(page: Page, live_server_url):
    # 1. Login
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Navigate to HR & Payroll
    page.get_by_role("button", name=re.compile("HR & Payroll")).click()
    page.get_by_role("link", name=re.compile("Staff Directory")).click()
    
    # Verify page loaded
    expect(page.locator("h1")).to_contain_text("Staff Members")

    # 3. Navigate to Staff Positions
    page.get_by_role("link", name=re.compile("Staff Positions")).click()
    expect(page.locator("h1")).to_contain_text("Staff Positions")

    # 4. Navigate to Payroll
    page.get_by_role("link", name=re.compile("Payroll Records")).click()
    expect(page.locator("h1")).to_contain_text("Payrolls")
