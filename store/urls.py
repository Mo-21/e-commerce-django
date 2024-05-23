from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('collections', views.CollectionViewSet)
router.register('products', views.ProductViewSet)
router.register('customers', views.CustomerViewSet)


urlpatterns = router.urls
