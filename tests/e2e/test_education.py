import pytest
import re
from playwright.sync_api import Page, expect

def test_education_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Prerequisites: Create Family and Member for Teacher
    # Create Family
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Add family").click()
    page.fill('input[name="name"]', "Edu Test Family")
    page.click("button[name='action-save']")
    
    # Create Member
    page.get_by_role("link", name="Members", exact=True).click()
    page.get_by_role("link", name="Add member").click()
    page.fill('input[name="first_name"]', "Teacher")
    page.fill('input[name="last_name"]', "One")
    if page.locator('select[name="family"]').is_visible():
        page.select_option('select[name="family"]', label="Edu Test Family")
    page.click("button[name='action-save']")
    
    # 3. Navigate to Education -> Teachers and Create Teacher
    page.get_by_role("button", name="Education").click()
    page.get_by_role("link", name="Teachers").click()
    page.get_by_role("link", name="Add Teacher").click()
    
    # Select Member
    # Inspecting model: OneToOne to Member. 
    # Usually a chooser or select.
    if page.locator('select[name="member"]').is_visible():
        page.select_option('select[name="member"]', label="Teacher One")
    else:
        # If chooser, might need to search. 
        # Assume select for now as per other tests.
        # If failure, we will see.
        pass
        
    page.fill('input[name="specialization"]', "Math")
    page.click("button[name='action-save']")
    
    # Verify Teacher
    expect(page.locator("text=Teacher: Teacher One")).to_be_visible()
    
    # 4. Create Class
    page.get_by_role("link", name="Classes").click()
    page.get_by_role("link", name="Add Class").click()
    
    page.fill('input[name="name"]', "Math 101")
    page.select_option('select[name="grade_level"]', value="high") # value from model choices
    page.select_option('select[name="subject"]', value="other") # value from model choices? 'other' is in tuple
    
    # Link Teacher
    if page.locator('select[name="teacher"]').is_visible():
        page.select_option('select[name="teacher"]', label="Teacher: Teacher One")
        
    page.click("button[name='action-save']")
    
    # Verify Class
    expect(page.locator("text=Math 101")).to_be_visible()
    
    # 5. Cleanup
    # Delete Class
    page.get_by_role("link", name="Math 101").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    # Delete Teacher
    page.get_by_role("link", name="Teachers").click()
    page.get_by_role("link", name="Teacher: Teacher One").click() # Link might correspond to str()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    # Delete Member and Family (Optional cleanup but good practice)
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Members", exact=True).click()
    page.get_by_role("link", name="Teacher One").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Edu Test Family").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
