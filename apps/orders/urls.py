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
    path('api/templates/', api.ContactTemplateListView.as_view(), name='api_templates'),
    path('api/templates/<int:pk>/', api.ContactTemplateDeleteView.as_view(), name='api_template_delete'),
    path('api/delivery-templates/', api.DeliveryTemplateListView.as_view(), name='api_delivery_templates'),
    path('api/delivery-templates/<int:pk>/', api.DeliveryTemplateDetailView.as_view(), name='api_delivery_template_detail'),
    path('api/cargo-templates/', api.CargoTemplateListView.as_view(), name='api_cargo_templates'),
    path('api/cargo-templates/<int:pk>/', api.CargoTemplateDeleteView.as_view(), name='api_cargo_template_delete'),
    path('api/address-suggest/', api.AddressSuggestView.as_view(), name='api_address_suggest'),
]
