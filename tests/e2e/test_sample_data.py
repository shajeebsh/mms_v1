import pytest
import re
from playwright.sync_api import Page, expect

def test_sample_data_navigation(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))
    
    # 2. Navigate
    page.get_by_role("link", name="Sample Data Management").click()
    
    # Verify
    expect(page.locator("h1")).to_contain_text("Sample Data Management")
    # Verify content
    expect(page.locator("text=Clear and Generate Sample Data")).to_be_visible()
