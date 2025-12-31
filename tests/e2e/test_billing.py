import pytest
import re
from playwright.sync_api import Page, expect

def test_billing_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # Need Family for Invoice? Yes model says optional but let's see.
    # Create Family
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Add family").click()
    page.fill('input[name="name"]', "Billing Test Family")
    page.click("button[name='action-save']")

    # 2. Create Invoice
    page.get_by_role("button", name="FINANCE & ACCOUNTS").click()
    page.get_by_role("link", name="Invoices").click()
    page.get_by_role("link", name="Add Invoice").click()
    
    page.fill('input[name="invoice_number"]', "INV-AUTO-001")
    page.fill('input[name="due_date"]', "2025-12-31")
    
    if page.locator('select[name="family"]').is_visible():
        page.select_option('select[name="family"]', label="Billing Test Family")
        
    page.click("button[name='action-save']")
    
    # Verify Invoice
    expect(page.locator("text=INV-AUTO-001")).to_be_visible()
    
    # 3. Create Billing Payment
    page.get_by_role("link", name="Billing Payments").click()
    page.get_by_role("link", name="Add Billing Payment").click()
    
    # Select Invoice
    if page.locator('select[name="invoice"]').is_visible():
        page.select_option('select[name="invoice"]', label="Invoice INV-AUTO-001 (Draft)") # Check str representation
    
    page.fill('input[name="amount"]', "100")
    page.select_option('select[name="payment_method"]', value="cash")
    
    page.click("button[name='action-save']")
    
    # Verify Payment
    expect(page.locator("text=Payment ₹100.00 for INV-AUTO-001")).to_be_visible()
    
    # 4. Cleanup
    page.get_by_role("link", name="Payment ₹100.00 for INV-AUTO-001").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Invoices").click()
    page.get_by_role("link", name="INV-AUTO-001").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("button", name="Membership").click()
    page.get_by_role("link", name="Families").click()
    page.get_by_role("link", name="Billing Test Family").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
