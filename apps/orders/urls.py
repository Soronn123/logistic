from django.urls import path

from . import api, views

app_name = 'orders'

urlpatterns = [
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('track/<slug:tracking_number>/', views.OrderTrackView.as_view(), name='track'),
    path('track/<slug:tracking_number>/door-delivery/', views.DoorDeliveryRequestView.as_view(), name='door_delivery'),
    path('track/<slug:tracking_number>/request-changes/', views.RequestChangesView.as_view(), name='request_changes'),
    path('api/<slug:tracking_number>/status/', api.OrderStatusUpdateView.as_view(), name='api_status'),
    path('api/<slug:tracking_number>/pickup/', api.OrderPickupConfirmView.as_view(), name='api_pickup'),
    path('api/<slug:tracking_number>/deliver/', api.OrderDeliveryConfirmView.as_view(), name='api_deliver'),
    path('api/<slug:tracking_number>/track/', api.OrderTrackingAPIView.as_view(), name='api_track'),
]
