from django.urls import include, path
from rest_framework import routers

from products import views

router = routers.DefaultRouter()
router.register('', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
