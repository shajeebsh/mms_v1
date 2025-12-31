import pytest
import re
from playwright.sync_api import Page, expect

def test_hr_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Prereq: Create Family & Member
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Add family").click()
    page.fill('input[name="name"]', "HR Test Family")
    page.click("button[name='action-save']")
    
    page.get_by_role("link", name="Members", exact=True).click()
    page.get_by_role("link", name="Add member").click()
    page.fill('input[name="first_name"]', "Staff")
    page.fill('input[name="last_name"]', "Member")
    if page.locator('select[name="family"]').is_visible():
        page.select_option('select[name="family"]', label="HR Test Family")
    page.click("button[name='action-save']")

    # 3. Create Staff Position
    page.get_by_role("button", name="HR & Payroll").click()
    page.get_by_role("link", name="Staff Positions").click()
    page.get_by_role("link", name="Add Staff Position").click()
    
    page.fill('input[name="name"]', "Imam") # Should be choice or text? Model says choices but is it free text field in admin?
    # Model: name = CharField(choices=POSITION_CHOICES, unique=True)
    # So it's a select? No, unique=True, choices usually rendered as select.
    # But choices are keys. 'imam'.
    # If using select:
    if page.locator('select[name="name"]').is_visible():
         page.select_option('select[name="name"]', value="imam")
    else:
         page.fill('input[name="name"]', "imam") # Fallback
         
    page.click("button[name='action-save']")
    
    # 4. Create Staff Member
    page.get_by_role("link", name="Staff Directory").click()
    page.get_by_role("link", name="Add Staff Member").click()
    
    if page.locator('select[name="member"]').is_visible():
        page.select_option('select[name="member"]', label="Staff Member")
        
    if page.locator('select[name="position"]').is_visible():
        page.select_option('select[name="position"]', label="Imam")
        
    page.fill('input[name="hire_date"]', "2025-01-01")
    
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Staff Member - Imam")).to_be_visible()
    
    # 5. Cleanup
    page.get_by_role("link", name="Staff Member - Imam").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Staff Positions").click()
    page.get_by_role("link", name="Imam").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    # Clean Member/Family
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Members", exact=True).click()
    page.get_by_role("link", name="Staff Member").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="HR Test Family").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
