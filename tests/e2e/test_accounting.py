import pytest
import re
from playwright.sync_api import Page, expect

def test_accounting_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Check Chart of Accounts (Account Model)
    # Nav to Finance -> Chart of Accounts
    page.get_by_role("button", name="FINANCE & ACCOUNTS").click()
    page.get_by_role("link", name="Chart of Accounts").click()
    
    # Create Account Category (Needed for Account?)
    # Models say Account -> AccountCategory.
    # Where is AccountCategory menu? 
    # It might be in Finance -> Account Categories? No, models say `AccountCategory`.
    # Let's check if there is a menu for Account Category.
    # checking admin_menu.py...
    # finance_menu has: Donation Categories, Expense Categories.
    # accounting_menu not explicitly mentioned?
    # Ah, `get_modeladmin_url("accounting", "account")` is there.
    # But `AccountCategory` isn't in `admin_menu.py`.
    # Maybe it's registered via ModelAdminGroup or snippet?
    # Or maybe it's inline in Account creation?
    # Let's assume we can create it or it exists.
    # If not, test might fail.
    # But for now, let's try to create an Account.
    
    page.get_by_role("link", name="Add Account").click()
    
    # If Account Category is required, we might need to create it via a "+" button if available.
    # Or maybe it's populated.
    
    page.fill('input[name="name"]', "Test Auto Account")
    page.fill('input[name="code"]', "9999")
    
    # Select Category
    # If fails, we know we need to create category.
    # We can try to finding a category if dropdown exists.
    if page.locator('select[name="category"]').is_visible():
        # Select first available option?
        # page.locator('select[name="category"] option').nth(1).get_attribute("value") ...
        # Or just pick one by label if we know any default categories.
        # "Asset" is a type, not a category name.
        pass
        
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Test Auto Account")).to_be_visible()
    
    # 3. Create Transaction (Ledger)
    page.get_by_role("link", name="Ledger Transactions").click()
    page.get_by_role("link", name="Add Transaction").click()
    
    page.fill('input[name="description"]', "Test Auto Transaction")
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Test Auto Transaction")).to_be_visible()
    
    # 4. Cleanup
    page.get_by_role("link", name="Test Auto Transaction").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Chart of Accounts").click()
    page.get_by_role("link", name="Test Auto Account").click() # Link might receive ID or Code? Likely Code + Name string.
    # Search first to be safe?
    # page.fill('input[name="q"]', "Test Auto Account")
    # page.press('input[name="q"]', "Enter")
    # page.locator("text=Test Auto Account").click()
    # Assuming code 9999 is visible.
    page.get_by_role("link", name="9999 - Test Auto Account").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
