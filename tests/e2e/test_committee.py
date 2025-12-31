import pytest
import re
from playwright.sync_api import Page, expect

def test_committee_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Prereq: Member
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Add family").click()
    page.fill('input[name="name"]', "Comm Test Family")
    page.click("button[name='action-save']")
    
    page.get_by_role("link", name="Members", exact=True).click()
    page.get_by_role("link", name="Add member").click()
    page.fill('input[name="first_name"]', "Trustee")
    page.fill('input[name="last_name"]', "User")
    if page.locator('select[name="family"]').is_visible():
        page.select_option('select[name="family"]', label="Comm Test Family")
    page.click("button[name='action-save']")

    # 3. Create Committee Type
    page.get_by_role("button", name="Committee & Minutes").click()
    page.get_by_role("link", name="Committee Types").click()
    page.get_by_role("link", name="Add Committee Type").click()
    page.fill('input[name="name"]', "Finance Committee")
    page.click("button[name='action-save']")
    
    # 4. Create Committee
    page.get_by_role("link", name="Committees").click()
    page.get_by_role("link", name="Add Committee").click()
    page.fill('input[name="name"]', "Test Committee")
    if page.locator('select[name="committee_type"]').is_visible():
        page.select_option('select[name="committee_type"]', label="Finance Committee")
    page.fill('input[name="established_date"]', "2025-01-01")
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Test Committee")).to_be_visible()
    
    # 5. Create Trustee
    page.get_by_role("link", name="Trustees").click()
    page.get_by_role("link", name="Add Trustee").click()
    if page.locator('select[name="member"]').is_visible():
        page.select_option('select[name="member"]', label="Trustee User")
    page.select_option('select[name="position"]', value="trustee")
    page.fill('input[name="appointed_date"]', "2025-01-01")
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Trustee User")).to_be_visible()
    
    # 6. Cleanup
    page.get_by_role("link", name="Trustee User").click() # Link logic
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Committees").click()
    page.get_by_role("link", name="Test Committee").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Committee Types").click()
    page.get_by_role("link", name="Finance Committee").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    # Clean Member
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Members", exact=True).click()
    page.get_by_role("link", name="Trustee User").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Comm Test Family").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
