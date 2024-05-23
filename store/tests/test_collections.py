from rest_framework.test import APIClient
from rest_framework import status
from model_bakery import baker
from store.models import Collection
import pytest


@pytest.mark.django_db
class TestCollections:
    def test_collection_creation_returns_403_if_user_is_not_staff(self, create_collection, authenticate_user):
        authenticate_user(is_staff=False)

        response = create_collection({'name': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_collection_list_returns_200_if_user_is_anon(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
