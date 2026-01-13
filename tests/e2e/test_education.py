import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_education_crud(page: Page, live_server_url):
    # 1. Login
    page.goto(f"{live_server_url}/cms/login/")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "adminpassword")
    page.click('button[type="submit"]')
    expect(page).to_have_title(re.compile("Dashboard"))

    # 2. Navigate to Education -> Classes
    page.get_by_role("button", name=re.compile("Education")).click()
    page.get_by_role("link", name=re.compile("Classes")).click()
    
    # Verify page loaded
    expect(page.locator("h1")).to_contain_text("Classes")

    # 3. Navigate to Teachers
    page.get_by_role("link", name=re.compile("Teachers")).click()
    expect(page.locator("h1")).to_contain_text("Teachers")

    # 4. Navigate to Enrollments
    page.get_by_role("link", name=re.compile("Student Enrollments")).click()
    expect(page.locator("h1")).to_contain_text("Student Enrollments")
