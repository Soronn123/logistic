from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('track/<slug:tracking_number>/', views.OrderTrackView.as_view(), name='track'),
    path('<slug:tracking_number>/door-delivery/', views.DoorDeliveryRequestView.as_view(), name='door_delivery'),
    path('<slug:tracking_number>/request-changes/', views.RequestChangesView.as_view(), name='request_changes'),
]
