import pytest
import re
from playwright.sync_api import Page, expect

def test_membership_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    
    # Wait for dashboard
    # Verify navigation to dashboard similar to test_auth.py
    expect(page).to_have_title(re.compile("Dashboard")) 
    # Or just "Dashboard" if partial match? expect(page).to_have_title(re.compile("Dashboard")) is better but needs re import.
    # Let's rely on text but maybe the text is different? "Welcome to the MMS" might be "Welcome to MMS" or something.
    expect(page.locator('h1')).to_contain_text("Dashboard")

    # 2. Navigate to Membership -> Families and Create a Family
    # Click on sidebar 'Membership' (it might be collapsed or just an icon depending on sidebar state, 
    # but initially we should see the text if expanded or hover)
    # Based on admin_menu.py it has label "🏠 Membership"
    
    # Using strict selectors to find the menu item
    page.click('a[href="/cms/membership/family/"]')  # Direct link might be cleaner if menu interaction is flaky, 
                                                     # but let's try to simulate user navigation if possible.
                                                     # If sidebar is dynamic, 'page.click' on the main menu might be needed.
                                                     # Let's assume the sidebar is open or we can click the main item.
    
    # Actually, simpler to just go to the URL directly for stability in this step, 
    # but the request was "test navigation". Let's try matching the text.
    
    # Click "Membership" group
    page.get_by_role("button", name="Membership").click()
    
    # Click "Families"
    page.get_by_role("link", name="Families").click()
    
    # Verify we are on Families page
    expect(page.locator("h1")).to_contain_text("Families")
    
    # Create Family
    page.get_by_role("link", name="Add family").click()
    page.fill('input[name="name"]', "Test Auto Family")
    page.fill('textarea[name="address"]', "123 Test St")
    page.click("button[name='action-save']")
    
    # Verify Family Created
    expect(page.locator("text=Test Auto Family")).to_be_visible()
    
    # 3. Navigate to Members and Create Member
    page.get_by_role("link", name="Members", exact=True).click()
    expect(page.locator("h1")).to_contain_text("Members")
    
    page.get_by_role("link", name="Add member").click()
    
    # Fill Member Details
    page.fill('input[name="first_name"]', "John")
    page.fill('input[name="last_name"]', "Doe")
    
    # Select Family (Autocomplete or Dropdown)
    # Wagtail foreign keys often use a chooser or a select. 
    # If it's a standard ForeignKey with FieldPanel, it might be a select. 
    # Inspecting models.py doesn't show the widget, but assuming standard select for now or autocomplete.
    # If it's a snippet chooser, it's different.
    # ModelAdmin usually uses standard django widgets unless configured otherwise.
    # Let's try filling if it's a select or interacting if it's a chooser.
    # Given 'FieldPanel("family")', it's likely a Select or a Chooser.
    # Let's assume standard Select for simplicity first, or try to select by label.
    
    # Note: If it's a select2 or similar, we might need to click and type.
    # Let's try to select the option "Test Auto Family"
    # page.select_option('select[name="family"]', label="Test Auto Family") 
    # But if standard Wagtail chooser:
    
    if page.locator('select[name="family"]').is_visible():
        page.select_option('select[name="family"]', label="Test Auto Family")
    else:
        # It might be a chooser widget
        # For now, let's assume it's a select for a start.
        # If it fails, I'll update it.
         page.select_option('select[name="family"]', label="Test Auto Family")

    # Other required fields? 
    # Models say: first_name, last_name, family. 
    # is_head_of_family default False.
    # gender blank=True
    
    page.click("button[name='action-save']")
    
    # 4. Read (Verify creation)
    expect(page.locator("text=John Doe")).to_be_visible()
    expect(page.locator("text=Test Auto Family")).to_be_visible()
    
    # 5. Update
    page.get_by_role("link", name="John Doe").click()
    page.fill('input[name="first_name"]', "Jane")
    page.click("button[name='action-save']")
    
    # Verify Update
    expect(page.locator("text=John Doe")).not_to_be_visible()
    expect(page.locator("text=Jane Doe")).to_be_visible()
    
    # 6. Delete Member
    page.get_by_role("link", name="Jane Doe").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']") # Confirm delete
    
    # Verify Member Deletion
    expect(page.locator("text=Jane Doe")).not_to_be_visible()
    
    # 7. Delete Family (Cleanup)
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Test Auto Family").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']") # Confirm delete
    
    expect(page.locator("text=Test Auto Family")).not_to_be_visible()

