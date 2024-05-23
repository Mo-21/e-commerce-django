from rest_framework.test import APIClient
from rest_framework import status
import pytest


@pytest.mark.django_db
class TestCollections:
    def test_collection_creation_returns_403_if_user_is_not_staff(self):
        collection = {'name': 'a'}

        client = APIClient()
        response = client.post('/store/collections/', collection)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_collection_list_returns_200_if_user_is_anon(self):
        collection_id = '6'

        api_client = APIClient()
        response = api_client.get('/store/products/1/')

        assert response.status_code == status.HTTP_200_OK
