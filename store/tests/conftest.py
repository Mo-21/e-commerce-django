from rest_framework.test import APIClient
from django.contrib.auth.models import User
from model_bakery import baker
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate_user(api_client):
    def do_authenticate_user(is_staff):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate_user


@pytest.fixture
def create_instance(request):
    def do_create_instance():
        return baker.make(request.cls.model)
    return do_create_instance
