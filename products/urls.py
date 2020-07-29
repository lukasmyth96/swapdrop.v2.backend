from django.urls import include, path
from rest_framework import routers

from products import views

router = routers.DefaultRouter()
router.register('', views.ProductViewSet)

urlpatterns = [
    path('products/', include(router.urls)),
    path('feed/', views.FeedListView.as_view(), name='feed'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
