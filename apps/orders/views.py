import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, TemplateView, View

from apps.geo.models import City

from .forms import OrderForm
from .models import Order, OrderStatusHistory
from .routing import (
    auto_assign_services,
    calculate_price,
    compute_eta,
    get_initial_status,
)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'pages/orders/create.html'
    success_url = reverse_lazy('users:orders')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.services.models import AdditionalService, Service
        cities_qs = City.objects.filter(is_active=True)
        context['cities'] = cities_qs
        context['services'] = Service.objects.filter(is_active=True)
        context['additional_services'] = AdditionalService.objects.all()
        context['cities_json'] = json.dumps([
            {
                'id': c.id,
                'name': str(c),
                'latitude': c.latitude,
                'longitude': c.longitude,
                'country': c.country,
            }
            for c in cities_qs
        ])
        context['default_lat'] = 55.7558
        context['default_lng'] = 37.6173

        # Compute auto-assignment rules for display on the services step
        context['auto_service_slugs'] = {
            'customs_duty': 'customs-duty',
            'customs_clearance': 'customs-clearance',
            'warehouse_transit': 'warehouse-transit',
            'last_mile_delivery': 'last-mile-delivery',
            'email_order_created': 'email-order-created',
            'email_customs_cleared': 'email-customs-cleared',
            'email_delivered': 'email-delivered',
            'extended_insurance': 'extended-insurance',
            'hand_carry': 'hand-carry',
            'adr_transport': 'adr-transport',
            'refrigerated_transport': 'refrigerated-transport',
            'truck_transport': 'truck-transport',
            'rail_transport': 'rail-transport',
        }
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        from_city = form.cleaned_data.get('sender_address')
        to_city = form.cleaned_data.get('recipient_address')
        weight = form.cleaned_data.get('weight') or 0
        service = form.cleaned_data.get('service')
        additional_services = form.cleaned_data.get('additional_services')
        declared_value = form.cleaned_data.get('declared_value')
        is_fragile = form.cleaned_data.get('is_fragile', False)
        is_dangerous = form.cleaned_data.get('is_dangerous', False)
        is_temperature_sensitive = form.cleaned_data.get('is_temperature_sensitive', False)

        # Auto-assign services based on cargo and route rules
        auto = auto_assign_services(
            from_city=from_city,
            to_city=to_city,
            weight=float(weight),
            length=form.cleaned_data.get('length'),
            width=form.cleaned_data.get('width'),
            height=form.cleaned_data.get('height'),
            declared_value=declared_value,
            is_fragile=is_fragile,
            is_dangerous=is_dangerous,
            is_temperature_sensitive=is_temperature_sensitive,
        )

        # Apply auto-assigned service if user didn't select one
        if not service and auto.get('service'):
            form.instance.service = auto['service']

        # Set additional services (merge user-selected with auto-assigned)
        user_addons = list(additional_services.all()) if additional_services else []
        auto_addons = auto.get('additional_services', [])
        all_addons = user_addons + [a for a in auto_addons if a not in user_addons]

        pricing = calculate_price(
            from_city, to_city, float(weight), form.instance.service or service,
            additional_services=None,
            declared_value=declared_value,
        )
        form.instance.total_price = pricing['total_price']
        form.instance.status = get_initial_status(from_city)
        form.instance.estimated_delivery_date = compute_eta(
            from_city, to_city, delivery_days=pricing['delivery_days']
        )

        response = super().form_valid(form)

        # Set additional services after save (m2m)
        if all_addons:
            self.object.additional_services.set(all_addons)

        OrderStatusHistory.objects.create(
            order=self.object,
            status=self.object.status,
            changed_by=self.request.user,
            comment=_('Order created'),
        )

        messages.success(
            self.request,
            _('Order %(tracking)s created successfully! You can track it in your orders.') % {
                'tracking': self.object.tracking_number,
            },
        )

        return response


class OrderTrackView(DetailView):
    model = Order
    template_name = 'pages/orders/track.html'
    context_object_name = 'order'
    slug_field = 'tracking_number'
    slug_url_kwarg = 'tracking_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.select_related('changed_by').order_by('timestamp')
        return context


class TrackingLookupView(TemplateView):
    template_name = 'pages/orders/tracking_lookup.html'

    def get(self, request, *args, **kwargs):
        tracking_number = request.GET.get('tracking_number', '').strip()
        if tracking_number:
            order = get_object_or_404(Order, tracking_number=tracking_number)
            return render(request, 'pages/orders/track.html', {
                'order': order,
                'status_history': order.status_history.select_related('changed_by').order_by('timestamp'),
            })
        return super().get(request, *args, **kwargs)


class TrackingPublicDetailView(DetailView):
    model = Order
    template_name = 'pages/orders/track.html'
    context_object_name = 'order'
    slug_field = 'tracking_number'
    slug_url_kwarg = 'tracking_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.select_related('changed_by').order_by('timestamp')
        return context


class DoorDeliveryRequestView(TemplateView):
    template_name = 'pages/orders/door_delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_number'] = self.kwargs.get('tracking_number', '')
        return context


class RequestChangesView(TemplateView):
    template_name = 'pages/orders/request_changes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_number'] = self.kwargs.get('tracking_number', '')
        return context
