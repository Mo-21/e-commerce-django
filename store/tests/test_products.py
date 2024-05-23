from store.models import Product, Collection
from model_bakery import baker
from .test_generic_models import GenericModelTests
import pytest


@pytest.mark.django_db
class TestProduct(GenericModelTests):
    model = Product
    endpoint = '/store/products/'

    @property
    def create_data(self):
        return {
            "title": "Product A",
            "description": "",
            "unit_price": 123.0,
            "price_with_tax": 184.5,
            "quantity": 41,
            "collection": int(self.collection.id)
        }

    @property
    def update_data(self):
        return {
            "title": "Product B",
            "description": "",
            "unit_price": 123.0,
            "price_with_tax": 184.5,
            "quantity": 1234,
            "collection": int(self.collection.id)
        }

    @pytest.fixture(autouse=True)
    def setup(self):
        self.collection = baker.make(Collection)
