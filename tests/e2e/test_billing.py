import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_billing_crud(page: Page, live_server_url):
    # 1. Login
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Navigate to Invoices (under FINANCE & ACCOUNTS menu)
    page.get_by_role("button", name=re.compile("FINANCE & ACCOUNTS")).click()
    page.get_by_role("link", name=re.compile("Invoices")).click()
    
    # Verify page loaded
    expect(page.locator("h1")).to_contain_text("Invoices")

    # 3. Navigate to Billing Payments
    page.get_by_role("link", name=re.compile("Billing Payments")).click()
    expect(page.locator("h1")).to_contain_text("Billing Payments")
