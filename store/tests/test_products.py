from store.models import Product, Collection, Promotion
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
            'title': 'Product A',
            'description': '',
            'unit_price': 123.0,
            'quantity': 41,
            'promotion': [],
            'collection': int(self.collection.id)
        }

    @property
    def update_data(self):
        return {
            'title': 'Product A',
            'description': '',
            'unit_price': 123.0,
            'quantity': 41,
            'promotion': [self.promotion.id],
            'collection': int(self.collection.id)
        }

    @pytest.fixture(autouse=True)
    def setup(self):
        self.collection = baker.make(Collection)
        self.promotion = baker.make(Promotion)
