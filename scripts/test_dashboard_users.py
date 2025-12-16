import requests

BASE = 'http://127.0.0.1:8000'
LOGIN = BASE + '/login/'
DASH = BASE + '/dashboard/'

users = {
    'admin': ['Site Admin', 'Wagtail CMS'],
    'membership_user': ['Members', 'Overdue Dues'],
    'finance_user': ['Record Donation', 'Financial Reports'],
    'education_user': ['Add Class', 'Teachers'],
    'assets_user': ['Shops', 'Property Units'],
    'operations_user': ['Auditorium Bookings', 'Prayer Times'],
    'hr_user': ['Staff Directory', 'Payroll'],
    'committee_user': ['Trustees', 'Meetings'],
}
PASSWORD = 'password123'

session = requests.Session()

results = {}
for username, expected in users.items():
    s = requests.Session()
    # Get login page to obtain csrf
    r = s.get(LOGIN, timeout=5)
    if r.status_code != 200:
        results[username] = f'LOGIN_PAGE_ERROR {r.status_code}'
        continue
    import re
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
    csrf = m.group(1) if m else ''
    data = {'username': username, 'password': PASSWORD, 'csrfmiddlewaretoken': csrf}
    headers = {'Referer': LOGIN}
    p = s.post(LOGIN, data=data, headers=headers, timeout=5, allow_redirects=True)
    if p.status_code not in (200, 302):
        results[username] = f'LOGIN_FAILED_HTTP_{p.status_code}'
        continue
    # fetch dashboard
    d = s.get(DASH, timeout=5)
    if d.status_code != 200:
        results[username] = f'DASH_ERROR_{d.status_code}'
        continue
    body = d.text
    missing = [e for e in expected if e not in body]
    if missing:
        results[username] = f'MISSING: {missing}'
    else:
        results[username] = 'OK'

for u, res in results.items():
    print(u, res)
