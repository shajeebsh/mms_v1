import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_data_profiling_view_superuser(admin_client):
    """Test that superuser can access data profiling view"""
    url = reverse('home_admin:data_profiling')
    response = admin_client.get(url)
    assert response.status_code == 200
    assert b"Data Profiling" in response.content
    assert b"Table Statistics" in response.content

@pytest.mark.django_db
def test_data_profiling_view_regular_user(client):
    """Test that regular user cannot access data profiling view"""
    user = User.objects.create_user(username='staff', password='password')
    client.login(username='staff', password='password')
    url = reverse('home_admin:data_profiling')
    response = client.get(url)
    # Since it's protected by user_passes_test(_is_superuser), it might redirect to login or return 302
    assert response.status_code == 302

@pytest.mark.django_db
def test_data_profiling_csv_export(admin_client):
    """Test that CSV export works for superuser"""
    url = reverse('home_admin:data_profiling') + "?export=csv"
    response = admin_client.get(url)
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'
    assert 'attachment; filename="data_profiling_' in response['Content-Disposition']
    content = response.content.decode('utf-8')
    assert "Module,Model Name,Record Count,Last Updated" in content
