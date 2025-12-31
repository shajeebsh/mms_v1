import pytest
import re
from playwright.sync_api import Page, expect

def test_assets_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Create Shop
    page.get_by_role("button", name="Assets").click()
    page.get_by_role("link", name="Shops").click()
    page.get_by_role("link", name="Add Shop").click()
    
    page.fill('input[name="name"]', "Test Auto Shop")
    page.select_option('select[name="shop_type"]', value="retail")
    page.fill('input[name="monthly_rent"]', "1000")
    
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Test Auto Shop (Retail Shop)")).to_be_visible()
    
    # 3. Create Property Unit
    page.get_by_role("link", name="Property Units").click()
    page.get_by_role("link", name="Add Property Unit").click()
    
    page.fill('input[name="name"]', "Unit 101")
    page.select_option('select[name="unit_type"]', value="apartment")
    page.fill('textarea[name="address"]', "Building A")
    
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Unit 101")).to_be_visible()
    
    # 4. Cleanup
    page.get_by_role("link", name="Unit 101").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Shops").click()
    page.get_by_role("link", name="Test Auto Shop").click() # Or logic to find it
    # If list display has name, it's clickable.
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
