from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from model_bakery import baker
from store.models import Collection
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
def update_collection(api_client, collection):
    collection = model_to_dict(collection)

    def do_update_collection():
        collection['name'] = 'a'
        collection['featured_product'] = ''
        id = collection['id']
        return api_client.put(
            f'/store/collections/{id}/', collection)
    return do_update_collection


@pytest.fixture
def collection():
    return baker.make(Collection)


@pytest.fixture
def authenticate_user(api_client):
    def do_authenticate_user(is_staff):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate_user
