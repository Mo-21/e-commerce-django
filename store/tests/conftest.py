from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post(
            '/store/collections/', collection)
    return do_create_collection


@pytest.fixture
def authenticate_user(api_client):
    def do_authenticate_user(is_staff):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate_user
