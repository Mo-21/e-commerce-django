from store.models import Collection
from .test_generic_models import GenericModelTests
import pytest


@pytest.mark.django_db
class TestCollection(GenericModelTests):
    model = Collection
    endpoint = '/store/collections/'
    create_data = {'name': 'a'}
    update_data = {'name': 'updated name', 'featured_product': ''}
