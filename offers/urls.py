from django.urls import path

from offers import views


urlpatterns = [

    path('make/', views.MakeOffer.as_view(), name='make-offer'),
    path('cancel/', views.CancelOffer.as_view(), name='cancel-offer'),
    path('reject/', views.RejectOffer.as_view(), name='reject-offer'),
    path('accept/', views.AcceptOffer.as_view(), name='accept-offer')
]
