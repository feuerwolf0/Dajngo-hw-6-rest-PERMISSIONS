import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_api(client):
    url = reverse('adv-list')
    print(url)
    response = client.get('/advertisements/')
    print('IWIOFWFKOJNWO')
    print(response.status_code)
    assert response.status_code == 200
