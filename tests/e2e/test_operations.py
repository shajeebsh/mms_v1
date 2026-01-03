import pytest
import re
from playwright.sync_api import Page, expect

def test_operations_crud(page: Page):
    # 1. Login
    page.goto("http://localhost:8000/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Create Auditorium Booking
    page.get_by_role("button", name="Operations").click()
    page.get_by_role("link", name="Auditorium Bookings").click()
    page.get_by_role("link", name="Add Auditorium Booking").click()
    
    page.fill('input[name="event_name"]', "Test Event")
    page.fill('input[name="organizer"]', "Test Org")
    page.fill('input[name="contact_person"]', "John")
    page.fill('input[name="contact_email"]', "test@example.com")
    page.fill('input[name="contact_phone"]', "1234567890")
    page.fill('input[name="booking_date"]', "2025-12-31")
    page.fill('input[name="start_time"]', "10:00")
    page.fill('input[name="end_time"]', "12:00")
    page.fill('input[name="expected_attendees"]', "100")
    page.fill('textarea[name="purpose"]', "Testing")
    
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Test Event")).to_be_visible()
    
    # 3. Create Prayer Time
    page.get_by_role("link", name="Prayer Times").click()
    page.get_by_role("link", name="Add Prayer Time").click()
    
    page.fill('input[name="date"]', "2025-12-31")
    page.select_option('select[name="prayer"]', value="fajr")
    page.fill('input[name="time"]', "05:00")
    
    page.click("button[name='action-save']")
    
    # Verify
    expect(page.locator("text=Fajr")).to_be_visible()
    
    # 4. Cleanup
    page.get_by_role("link", name="Fajr").first.click() # might be multiple, carefully select
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
    
    page.get_by_role("link", name="Auditorium Bookings").click()
    page.get_by_role("link", name="Test Event").click()
    page.get_by_role("link", name="Delete").click()
    page.click("button[type='submit']")
