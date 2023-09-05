import pytest
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from advertisements.models import Advertisement


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin():
    return User.objects.create_user('admin')


# @pytest.mark.django_db
# def test_api(client, admin):
#     url = reverse('adv-list')
#     Advertisement.objects.create(creator=admin, title='just', description='dect', draft='NO')
#     adv = Advertisement.objects.all()
#     response = client.get(url)
#     # print(response.data)
#
#     assert response.status_code == 200
#     assert len(response.data) == 1

