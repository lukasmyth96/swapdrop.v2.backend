from django.urls import include, path
from rest_framework import routers

from offers import views


urlpatterns = [

    path('make/', views.MakeOffer.as_view(), name='make-offer'),
]
