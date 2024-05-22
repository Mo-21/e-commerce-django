from rest_framework.viewsets import ModelViewSet
from .serializers import CollectionSerializer
from .models import Collection


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
