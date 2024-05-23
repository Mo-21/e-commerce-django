from rest_framework import status
import pytest


@pytest.mark.django_db
class GenericModelTests:
    model = None
    endpoint = None
    create_data = None
    update_data = None

    def test_creation_returns_401_if_user_is_anon(self, api_client):
        response = api_client.post(self.endpoint, self.create_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_creation_returns_403_if_user_is_not_staff(self, api_client, authenticate_user):
        authenticate_user(is_staff=False)
        response = api_client.post(self.endpoint, self.create_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_creation_returns_201_if_user_is_staff(self, api_client, authenticate_user):
        authenticate_user(is_staff=True)
        response = api_client.post(self.endpoint, self.create_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_returns_401_if_user_is_anon(self, api_client, create_instance):
        instance = create_instance()
        response = api_client.put(
            f'{self.endpoint}{instance.id}/', self.update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_returns_403_if_user_is_not_staff(self, api_client, authenticate_user, create_instance):
        authenticate_user(is_staff=False)
        instance = create_instance()
        response = api_client.put(
            f'{self.endpoint}{instance.id}/', self.update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_returns_200_if_user_is_staff(self, api_client, authenticate_user, create_instance):
        authenticate_user(is_staff=True)
        instance = create_instance()
        response = api_client.put(
            f'{self.endpoint}{instance.id}/', self.update_data)
        assert response.status_code == status.HTTP_200_OK

    def test_delete_returns_401_if_user_is_anon(self, api_client, create_instance):
        instance = create_instance()
        response = api_client.delete(f'{self.endpoint}{instance.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_returns_403_if_user_is_not_staff(self, api_client, authenticate_user, create_instance):
        authenticate_user(is_staff=False)
        instance = create_instance()
        response = api_client.delete(f'{self.endpoint}{instance.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_returns_204_if_user_is_staff(self, api_client, authenticate_user, create_instance):
        authenticate_user(is_staff=True)
        instance = create_instance()
        response = api_client.delete(f'{self.endpoint}{instance.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list_returns_200_if_user_is_anon(self, api_client):
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_returns_200_if_user_is_anon(self, api_client, create_instance):
        instance = create_instance()
        response = api_client.get(f'{self.endpoint}{instance.id}/')
        assert response.status_code == status.HTTP_200_OK
