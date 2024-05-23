from rest_framework.viewsets import ModelViewSet
from django.db.models.aggregates import Count
from .serializers import CollectionSerializer
from .models import Collection


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('product')
    ).all()
    serializer_class = CollectionSerializer
