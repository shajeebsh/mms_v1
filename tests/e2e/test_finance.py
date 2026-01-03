import pytest
import re
from playwright.sync_api import Page, expect

def test_finance_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Navigate to Finance -> Donation Categories and Create One
    # Click "FINANCE & ACCOUNTS" group (label might be different)
    page.get_by_role("button", name="FINANCE & ACCOUNTS").click()
    page.get_by_role("link", name="Donation Categories").click()
    
    page.get_by_role("link", name="Add donation category").click()
    page.fill('input[name="name"]', "Test Auto Category")
    page.click("button[name='action-save']")
    expect(page.locator("text=Test Auto Category")).to_be_visible()
    
    # 3. Create Donation
    page.get_by_role("link", name="Donations", exact=True).click()
    page.get_by_role("link", name="Add donation").click()
    
    # Fill Donation Details
    page.fill('input[name="amount"]', "100")
    
    # Select Category
    # Assuming standard select or choose via label
    if page.locator('select[name="category"]').is_visible():
        page.select_option('select[name="category"]', label="Test Auto Category")
    
    # Member is optional, skip for now or select if easy
    
    page.click("button[name='action-save']")
    
    # Verify Donation
    expect(page.locator("text=Test Auto Category")).to_be_visible()
    expect(page.locator("text=100.00")).to_be_visible()
    
    # 4. Edit Donation
    # Finding the link might be tricky if there is no specific text to click, but usually the first column is a link.
    # In list_display ('member', 'amount', 'donation_type', 'date', 'category')
    # If member is None, amount or date might be the link? 
    # Or Wagtail puts the link on the first column defined. 
    # 'member' allows null. If null, what is the link text? 'None'? 
    # Let's check if we can click by amount text.
    # Or we can just click "Edit" button if available (usually not valid in list view).
    # Wagtail list view makes the first column clickable. 
    # If member is None, it might show "(None)" or similar.
    # Let's try creating with a member if possible to ensure we have a link, 
    # BUT existing members might not be reliable unless we create one here.
    # So let's rely on finding the row and clicking.
    
    # Let's assume we can click "100.00" or similar? No, amount is not always a link.
    # To be safe, for this test let's Create Donation with a Note/Receipt that we can click?
    # search_fields = ('member__first_name', 'member__last_name', 'notes', 'receipt_number')
    # But receipt_number is not in list_display by default? No, it's not.
    
    # Let's adjust step 3 to add a member or just try to click the row.
    # Actually, simpler: verify creation and delete from list using "select all" or similar if needed?
    # No, we need to enter edit view to delete usually, OR checkbox select -> delete.
    
    # Implementation detail: Wagtail checks first column. 'member'. If None?
    # Let's create an expense first as well? 
    
    # Modification: Create Member first? Or just skip member.
    # If member is None, maybe it says "None".
    # page.get_by_text("None").first.click() -> might be ambiguous.
    
    # Better strategy: Add Receipt Number to list_display? No, I shouldn't modify code just for test unless needed.
    # Wait, 'member' is the first column.
    # If I create a donation without a member, the link text is probably "(None)" or "-"
    # Let's try to pass `receipt_number`? No, it's auto-generated mostly? No, blank=True in model, manual entry possible?
    # Model says receipt_number is CharField(blank=True).
    # Create with a note? Notes not in list_display.
    
    # Solution: Create a Member in Finance Test? 
    # Or assume "Test Auto Category" is clickable? 'category' is in list_display but is it the link?
    # No, usually only first column.
    
    # Let's click the first row's link.
    page.locator("table.listing tbody tr").first.locator("td").first.locator("a").click()
    
    # Update
    page.fill('input[name="amount"]', "150")
    page.click("button[name='action-save']")
    expect(page.locator("text=150.00")).to_be_visible()
    
    # Delete Donation
    page.locator("table.listing tbody tr").first.locator("td").first.locator("a").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    # 5. Cleanup Category
    page.get_by_role("link", name="Donation Categories").click()
    page.get_by_role("link", name="Test Auto Category").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")

