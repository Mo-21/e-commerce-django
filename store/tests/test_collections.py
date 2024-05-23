from rest_framework import status
import pytest


@pytest.mark.django_db
class TestCollections:
    def test_collection_creation_returns_401_if_user_is_anon(self, create_collection):
        response = create_collection({'name': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_collection_creation_returns_403_if_user_is_not_staff(self, create_collection, authenticate_user):
        authenticate_user(is_staff=False)

        response = create_collection({'name': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, create_collection, authenticate_user):
        authenticate_user(is_staff=True)

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_collections_list_returns_200_if_user_is_anon(self, api_client):
        response = api_client.get('/store/collections/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSingleCollection:
    def test_collection_update_returns_401_if_user_is_anon(self, update_collection):
        response = update_collection()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_collection_update_returns_403_if_user_is_not_staff(self, authenticate_user, update_collection):
        authenticate_user(is_staff=False)

        response = update_collection()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_collection_update_returns_200_if_user_is_staff(self, authenticate_user, update_collection):
        authenticate_user(is_staff=True)

        response = update_collection()

        assert response.status_code == status.HTTP_200_OK

    def test_collection_delete_returns_401_if_user_is_anon(self, delete_collection):
        response = delete_collection()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_collection_delete_returns_403_if_user_is_staff(self, authenticate_user, delete_collection):
        authenticate_user(is_staff=False)

        response = delete_collection()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_collection_delete_returns_200_if_user_is_staff(self, authenticate_user, delete_collection):
        authenticate_user(is_staff=True)

        response = delete_collection()

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_collection_retrieve_returns_200_if_user_is_anon(self, collection, api_client):
        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
